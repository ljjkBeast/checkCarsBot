import pymongo

db_client = pymongo.MongoClient("mongodb://localhost:27017/")

current_db = db_client["checkCarsBot"]

collection = current_db["users"]