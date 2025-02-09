from pymongo import MongoClient
from bson.objectid import ObjectId
from services.pokemon_api import get_growrate, get_nature, get_pokemon, get_gender
import random

client = MongoClient("mongodb+srv://mewtumew1:hoihoihoi@cluster0.jpxvquh.mongodb.net/test")
db = client["Pointlink"] 
owner_coll = db["owner"] 

def nicknamePet(userId,species, name):
    
