import pymongo
from pymongo import MongoClient
import config

def get_db():
    # Create a MongoDB client using the URI from config.py
    client = MongoClient(config.MONGO_URI)
    db = client['pokemon_db']  # Create or connect to the database 'pokemon_db'
    return db
