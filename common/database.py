import pymongo


class Database(object):
    URI = 'mongodb://127.0.0.1:27017'
    DATABASE = None

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
        Database.DATABASE = client["Thedoors"]

    # @staticmethod
    # def initialize_test():
    #     client = pymongo.MongoClient(Database.URI)
    #     Database.DATABASE = client["ThedoorsTest"]

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert_one(data)

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
