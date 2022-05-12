import sched, time

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client['tgbot']
collection = db['users']

