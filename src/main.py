from logger import Logger
from config import Configuration
from scrapper import PlacesScrapper


def main():
    logger = Logger()
    config = Configuration()

    PlacesScrapper(config, logger)


main()
