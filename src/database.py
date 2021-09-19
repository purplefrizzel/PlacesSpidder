from stem.util import conf
from config import Configuration
import pymongo


class Database():

    def __init__(self, config: Configuration):
        with pymongo.MongoClient("mongodb://" + config.getMongoUser() + ":" + config.getMongoPassword() + config.getMongoAddress() + ":" + config.getMongoPort()) as mongoClient:
            self.db = mongoClient[config.getMongoDatabase()]
            self.placesCol = self.db[config.getMongoCollection()]
