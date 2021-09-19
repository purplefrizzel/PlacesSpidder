import os
from database import Database
from requests.models import Response
from config import Configuration
import requests
from bs4 import BeautifulSoup
from stem.control import Controller
from logger import Logger


class PlacesScrapper():

    def __init__(self, config: Configuration, logger: Logger) -> None:
        self.config = config
        self.logger = logger
        self.pageNum = 1
        self.scrapComplete = False

        session = requests.session()
        session.proxies = {"http": "socks5://" + config.getTorAddress() + ":" + config.getTorPort(),
                           "https": "socks5://" + config.getTorAddress() + ":" + config.getTorPort()}
        self.session = session

        with Controller.from_port(address=config.getTorControllerAddress(), port=config.getTorControllerPort()) as self.controller:
            self.controller.authenticate(config.getTorControllerPassword())
            self.controller.drop_guards()
            self.controller.new_circuit()

        self.__begin()

    def __begin(self):
        res = self.__makeHttpRequest()
        soup = self.__parse(res)
        self.maxPageNum = int(self.__findTotalPages(soup))
        self.__findPlaces(soup)

    def __findTotalPages(self, soup: BeautifulSoup):
        self.logger.verbose("Looking for total number of pages.")
        pageNumbers = soup.select("body main div ul a")
        last = len(pageNumbers) - 1

        num: str = ""
        for char in pageNumbers[last].get("href"):
            if char.isdigit():
                num += char

        self.logger.verbose("Total number of pages found " + num)
        return num

    def __makeHttpRequest(self) -> Response:
        url = "https://www.lonelyplanet.com/places?page=" + \
            str(self.pageNum) + "&type=City"
        self.logger.verbose("Making HTTP Get Request to " +
                            url)
        res = self.session.get(
            url, headers={"User-Agent": "Places-Spider/0.0.1"})

        if res.ok == True:
            self.logger.verbose("HTTP Get Request to " + url +
                                " was successful with status code " + str(res.status_code))
            return res
        else:
            self.logger.error("HTTP Request failed to " + url +
                              " with status code " + str(res.status_code))

    def __parse(self, page: Response):
        self.logger.verbose("Beginning to parse page " + str(self.pageNum))

        return BeautifulSoup(page.content, "html.parser")

    def __findPlaces(self, soup: BeautifulSoup):
        places = soup.select("body main div ul a")
        last = len(places) - 1

        currentPlaceIndex = 0
        with open("places.list", "a") as file:
            for place in places:
                currentPlaceIndex += 1
                if place.get("href").__contains__("?page=") != True:
                    if place.get("href").__contains__("/undefined") == False:
                        file.write("https://www.lonelyplanet.com" +
                                   place.get("href") + "\n")

                if currentPlaceIndex == last:
                    file.close()
                    self.__nextPage()

    def __nextPage(self):
        if self.pageNum != self.maxPageNum:
            self.logger.verbose("Moving on to next page. \n")
            self.pageNum += 1
            self.__begin()
        else:
            self.scrapComplete = True
            self.logger.info("Max page reached. \n")
            self.__startScrapper()

    def __startScrapper(self):
        os.chdir("./")
        with open("places.list", "r") as file:
            urls = file.read().split("\n")
            for url in urls:
                if url == None or url == "" or url == "\n":
                    self.logger.verbose("URL not valid, skipping.")
                else:
                    PlaceScrapper(self.config, self.logger, url)


class PlaceScrapper():

    def __init__(self, config: Configuration, logger: Logger, placeUrl: str):
        self.name = placeUrl
        self.URL = placeUrl
        self.config = config
        self.logger = logger

        session = requests.session()
        session.proxies = {"http": "socks5://" + config.getTorAddress() + ":" + config.getTorPort(),
                           "https": "socks5://" + config.getTorAddress() + ":" + config.getTorPort()}
        self.session = session

        with Controller.from_port(address=config.getTorControllerAddress(), port=config.getTorControllerPort()) as self.controller:
            self.controller.authenticate(config.getTorControllerPassword())
            self.controller.drop_guards()
            self.controller.new_circuit()

        self.database = Database(config)

        self.__begin()

    def __begin(self):
        self.logger.info("Scrapper Starting for " + self.name)
        self.__store(self.__stripData(self.__parse(self.__makeHttpRequest())))

    def __parse(self, page: Response) -> BeautifulSoup:
        if page == None:
            return

        self.logger.verbose("(" + self.name + ")" +
                            " Beginning to parse page.")

        return BeautifulSoup(page.content, "html.parser")

    def __makeHttpRequest(self) -> Response:
        self.logger.verbose("Making HTTP Get Request to " + self.URL)
        res = self.session.get(
            self.URL, headers={"User-Agent": "Places-Spider/0.0.1"})

        if res.ok == True:
            self.logger.verbose("HTTP Get Request to " + self.URL +
                                " was successful with status code " + str(res.status_code))
            return res
        else:
            self.logger.error("HTTP Request failed to " + self.URL +
                              " with status code " + str(res.status_code))

    def __stripData(self, soup: BeautifulSoup) -> dict:
        self.logger.verbose("(" + self.name + ")" +
                            " Strippping data from page.")
        metas = soup.select("meta")

        place = {"name": "", "country": "", "continent": "",
                 "description": "", "image_url": "", "lp_url": ""}

        for meta in metas:
            if meta.get("property") == "og:image":
                place.update({"image_url": meta.get("content")})
            elif meta.get("name") == "description":
                split = meta.get("content").split("|")
                if len(split) != 1:
                    description = meta.get("content").split("|")[
                        1].replace(" ", "", 1)
                    place.update({"description": description})
            elif meta.get("property") == "og:title":
                title = meta.get("content").replace(
                    "travel", "").removesuffix(" ")
                place.update({"name": title})
            elif meta.get("name") == "title":
                split = meta.get("content").split("|")
                country = split[1].split(",")[0].replace(" ", "", 1)
                if len(split) >= 1 & split[1].__contains__(",") == True:
                    continent = split[1].split(",")[1].replace(" ", "", 1)
                else:
                    continent = split[1].replace(" ", "", 1)
                place.update({"country": country})
                place.update({"continent": continent})
            elif meta.get("property") == "og:url":
                if meta.get("content").__contains__("https://www.lonelyplanet.com/undefined") != True:
                    place.update({"lp_url": meta.get("content")})

        return place

    def __store(self, data: dict):
        self.logger.verbose("(" + self.name + ")" + " Storing data from page.")
        query = {"name": data["name"],
                 "country": data["country"], "lp_url": data["lp_url"]}

        if self.database.placesCol.find_one(query) == None:
            self.database.placesCol.insert_one(data)
            self.logger.verbose("(" + self.name + ")" + " Data stored. \n")
        else:
            self.logger.info("(" + self.name + ")" +
                             " Data already stored, skipping. \n")
