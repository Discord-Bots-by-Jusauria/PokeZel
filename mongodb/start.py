from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

from mongodb.pokemon import create_new_Pokemon
# Stelle sicher, dass du hier deinen Connection-String einträgst
client = MongoClient("mongodb+srv://mewtumew1:hoihoihoi@cluster0.jpxvquh.mongodb.net/test")
db = client["PokeZel"]  # Beispiel: Datenbankname

trainers_coll = db["trainers"]   # Collection für Spieler/Trainer
pokemons_coll = db["pokemons"]   # Collection für Pokémon

def create_trainer(user_id: int,name: str) -> dict:

    new_trainer = {
    "user_id": user_id,
    "name":name,
    "team": [],  # Placeholder field
    "dollar": 0,
    "role": 'trainer',
    "shiny_count": 0,
    "started":int( datetime.now().timestamp()),  # Current date and time in ISO 8601 format
    "fav": "none",
    "passive": "none",
    "badges": "none",
    "trainer_lvl": 1,
    "story":"start",
    "location":"Azurquora"
}
    result = trainers_coll.insert_one(new_trainer)
    return trainers_coll.find_one({"_id": result.inserted_id})

def create_starter_pokemon_for_trainer(user_id: int, pokemon_name: str) -> ObjectId:
    new_pokemon = create_new_Pokemon(pokemon_name,5)
    new_pokemon["was_in_team"] = True
    new_pokemon["nickname"]=f"{pokemon_name} the chosen one"
    trainer_pokemon ={
        "user_id": user_id,
        "pokemons_owned":[
            new_pokemon
        ]
    }
    result = pokemons_coll.insert_one(trainer_pokemon)
    return result.inserted_id

def update_trainer_team(trainer_id: ObjectId, pokemon_id: ObjectId):
    """
    Fügt den Pokémon-ID in die team-Liste des Trainers ein.
    """
    trainers_coll.update_one(
        {"_id": trainer_id},
        {"$push": {"team": {"pokemon_id": pokemon_id}}}  # Use a string key
    )
