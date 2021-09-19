import os
from bs4 import BeautifulSoup


class Configuration():

    def __init__(self):
        os.chdir("./")
        with open("config.xml") as file:
            self.doc = BeautifulSoup(file.read(), "xml")

    def getTorAddress(self) -> str:
        tor = self.doc.find("tor")
        return str(tor.find("address").getText())

    def getTorPort(self) -> str:
        tor = self.doc.find("tor")
        return str(tor.find("port").getText())

    def getTorControllerAddress(self) -> str:
        tor = self.doc.find("tor")
        controller = tor.find("controller")
        return controller.find("address").getText()

    def getTorControllerPort(self) -> int:
        tor = self.doc.find("tor")
        controller = tor.find("controller")
        return int(controller.find("port").getText())

    def getTorControllerPassword(self) -> str:
        tor = self.doc.find("tor")
        controller = self.doc.find("controller")
        return controller.find("password").getText()

    def getMongoDatabase(self):
        mongo = self.doc.find("mongo")
        return mongo.find("database").getText()

    def getMongoCollection(self):
        mongo = self.doc.find("mongo")
        return mongo.find("collection").getText()

    def getMongoAddress(self):
        mongo = self.doc.find("mongo")
        return mongo.find("address").getText()

    def getMongoPort(self):
        mongo = self.doc.find("mongo")
        return mongo.find("port").getText()

    def getDevMode(self) -> bool:
        return bool(self.doc.find("dev"))

    def getMongoUser(self) -> str:
        mongo = self.doc.find("mongo")
        return mongo.find("user").getText()

    def getMongoPassword(self) -> str:
        mongo = self.doc.find("mongo")
        return mongo.find("password").getText()
