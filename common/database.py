import pymongo
import os

class Database(object):
    URI = 'mongodb://127.0.0.1:27017'
    DATABASE = None
    SIMULATION = None

    @staticmethod
    def dropAll():
        Database.DATABASE['users'].drop()
        Database.DATABASE['orders'].drop()
        Database.DATABASE['schedules'].drop()
        Database.DATABASE['rooms'].drop()
        Database.DATABASE['facilities'].drop()
        Database.DATABASE['friends'].drop()

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        # client = pymongo.MongoClient(os.getenv("CUSTOMCONNSTR_MONGOURL"))
        Database.DATABASE = client["TheDoors"]
        # Database.DATABASE.authenticate(name=os.getenv("CUSTOMCONNSTR_MONGO_USERNAME"),password=os.getenv("CUSTOMCONNSTR_MONGO_PASSWORD"))
        Database.SIMULATION = client["Simulation"]

    # @staticmethod
    # def initialize_test():
    #     client = pymongo.MongoClient(Database.URI)
    #     Database.DATABASE = client["ThedoorsTest"]

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def update(collection, query, update):
        Database.DATABASE[collection].update(query, update)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def remove(collection, query):
        Database.DATABASE[collection].remove(query)

    @staticmethod
    def count(collection):
        return Database.DATABASE[collection].count()

############################### FOR THE SIMULATION ###############################

    @staticmethod
    def dropAllSimulation():
        Database.SIMULATION['users'].drop()
        Database.SIMULATION['orders'].drop()
        Database.SIMULATION['schedules'].drop()
        Database.SIMULATION['rooms'].drop()
        Database.SIMULATION['facilities'].drop()
        Database.SIMULATION['friends'].drop()

    # @staticmethod
    # def initialize():
    #     client = pymongo.MongoClient(Database.URI)
    #     Database.SIMULATION = client["Simulation"]

    @staticmethod
    def insertSimulation(collection, data):
        Database.SIMULATION[collection].insert(data)

    @staticmethod
    def findSimulation(collection, query):
        return Database.SIMULATION[collection].find(query)

    @staticmethod
    def updateSimulation(collection, query, update):
        Database.SIMULATION[collection].update(query, update)

    @staticmethod
    def find_oneSimulation(collection, query):
        return Database.SIMULATION[collection].find_one(query)

    @staticmethod
    def removeSimulation(collection, query):
        Database.SIMULATION[collection].remove(query)

    @staticmethod
    def countSimulation(collection):
        return Database.SIMULATION[collection].count()


