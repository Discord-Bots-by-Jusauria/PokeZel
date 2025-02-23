from pymongo import MongoClient
from bson.objectid import ObjectId
import random

client = MongoClient("mongodb+srv://mewtumew1:hoihoihoi@cluster0.jpxvquh.mongodb.net/test")
db = client["Pointlink"] 
owner_coll = db["owner"] 

def nicknamePet(user_id, name):
    return owner_coll.update_one({"user_id":user_id},{"$set":{"pet.0.nickname": name}})

def update_pet(user_id, pet):
    return owner_coll.update_one({"user_id":user_id},{"$set":{"pet.0": pet}})