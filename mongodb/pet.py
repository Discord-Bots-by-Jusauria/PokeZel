from pymongo import MongoClient
from bson.objectid import ObjectId
import random

client = MongoClient("mongodb+srv://mewtumew1:hoihoihoi@cluster0.jpxvquh.mongodb.net/test")
db = client["Pointlink"] 
owner_coll = db["owner"] 

def nicknamePet(userId, name):
    return owner_coll.update_one({"user_id":userId},{"$set":{"pet.0.nickname": name}})
