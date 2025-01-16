from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
# Stelle sicher, dass du hier deinen Connection-String einträgst
client = MongoClient("mongodb+srv://mewtumew1:hoihoihoi@cluster0.jpxvquh.mongodb.net/test")
db = client["PokeZel"]  # Beispiel: Datenbankname

trainers_coll = db["trainers"]   # Collection für Spieler/Trainer
pokemons_coll = db["pokemons"]   # Collection für Pokémon


def get_trainer(user_id: int) -> dict:
    """
    Sucht in der 'trainers'-Collection nach einem Trainer mit gegebener user_id.
    Gibt den Trainer als Dictionary zurück oder None, wenn keiner existiert.
    """
    return trainers_coll.find_one({"user_id": user_id})

def create_trainer(user_id: int,name: str) -> dict:
    new_trainer = {
    "user_id": user_id,
    "name":name,
    "team": [],  # Placeholder field
    "dollar": 0,
    "role": 'trainer',
    "shiny_count": 0,
    "started": datetime.now().isoformat(),  # Current date and time in ISO 8601 format
    "fav": "none",
    "passive": "none",
    "bages": "none",
    "lvl": 1
}
    result = trainers_coll.insert_one(new_trainer)
    return trainers_coll.find_one({"_id": result.inserted_id})

def create_starter_pokemon_for_trainer(user_id: int, pokemon_name: str) -> ObjectId:
    """
    Legt ein neues Pokémon-Dokument an und gibt dessen _id zurück.
    Dieses Pokémon gehört dem Spieler mit user_id.
    """
    new_pokemon = {
        "user_id": user_id,
        pokemons_owned:[
            {"name": pokemon_name,
        "nickname": pokemon_name+" the chosen one", 
        "lvl": 5,
        "gender": "unbekannt",
        "trust_level": 0,
        "motivation": 50,
        "happiness": 50,
        "stats": {"attack": 10, "defense": 10, "speed": 10},
        "exp_until_next_level": 100,
        "held_item": None,
        "passive_training": False}
        ],
    }
    result = pokemons_coll.insert_one(new_pokemon)
    return result.inserted_id

def update_trainer_team(trainer_id: ObjectId, pokemon_id: ObjectId):
    """
    Fügt den Pokémon-ID in die team-Liste des Trainers ein.
    """
    trainers_coll.update_one(
        {"_id": trainer_id},
        {"$push": {"team": pokemon_id}}
    )