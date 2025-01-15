from pymongo import MongoClient
from bson.objectid import ObjectId

# Stelle sicher, dass du hier deinen Connection-String einträgst
client = MongoClient("mongodb://USERNAME:PASSWORT@HOST:PORT")
db = client["mybotdb"]  # Beispiel: Datenbankname

trainers_coll = db["trainers"]   # Collection für Spieler/Trainer
pokemons_coll = db["pokemons"]   # Collection für Pokémon

def create_or_get_trainer(user_id: int) -> dict:
    """
    Sucht in der 'trainers'-Collection nach einem Trainer
    mit gegebener user_id. Falls keiner existiert, wird einer erstellt.
    """
    trainer = trainers_coll.find_one({"user_id": user_id})
    if not trainer:
        new_trainer = {
            "user_id": user_id,
            "team": [],       # Platzhalter, fügen wir später Pokémon-IDs hinzu
            # Weitere Felder je nach Bedarf:
            # "name": "???",
            # "gender": "???",
            # ...
        }
        result = trainers_coll.insert_one(new_trainer)
        trainer = trainers_coll.find_one({"_id": result.inserted_id})
    return trainer

def create_pokemon_for_trainer(user_id: int, pokemon_name: str) -> ObjectId:
    """
    Legt ein neues Pokémon-Dokument an und gibt dessen _id zurück.
    Dieses Pokémon gehört dem Spieler mit user_id.
    """
    new_pokemon = {
        "user_id": user_id,
        "name": pokemon_name,
        "nickname": pokemon_name,  # oder leer, wenn du Spitznamen erlaubst
        "lvl": 5,
        "gender": "unbekannt",
        "trust_level": 0,
        "motivation": 50,
        "happiness": 50,
        "stats": {"attack": 10, "defense": 10, "speed": 10},
        "exp_until_next_level": 100,
        "held_item": None,
        "pokemon_api_url": f"https://example.com/pokemon/{pokemon_name.lower()}",
        "passive_training": False,
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