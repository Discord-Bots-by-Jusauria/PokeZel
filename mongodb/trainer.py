from pymongo import MongoClient
from bson.objectid import ObjectId
# Stelle sicher, dass du hier deinen Connection-String einträgst
client = MongoClient("mongodb+srv://mewtumew1:hoihoihoi@cluster0.jpxvquh.mongodb.net/test")
db = client["PokeZel"]  # Beispiel: Datenbankname

trainers_coll = db["trainers"]   # Collection für Spieler/Trainer
pokemons_coll = db["pokemons"]   # Collection für Pokémon

def get_trainer_with_team(user_id: int) -> dict:
    """
    Fetches the trainer's details, including the Pokémon team with full details.
    """
    # Fetch the trainer document
    trainer = trainers_coll.find_one({"user_id": user_id})
    if not trainer:
        return None  # Trainer not found

    # Resolve Pokémon details for each Pokémon in the team
    team_with_details = []
    for team_entry in trainer.get("team", []):
        pokemon = pokemons_coll.find_one({"user_id":user_id})
        if pokemon:
            for poke in pokemon.get("pokemons_owned", []):
                if poke["id"]== team_entry["pokemon_id"]:
                    team_with_details.append({
                        "id": str(poke.get("id")),  # Add Pokémon object ID
                        "nickname": poke.get("nickname"),
                        "lvl": poke.get("lvl"),
                        "name": poke.get("name")
                    })

    # Add detailed team to the trainer object
    trainer["team"] = team_with_details
    return trainer


def update_whole_trainer_data(trainer: dict) -> bool:
    """
    Overwrites the entire trainer document with new data.
    """
    result = trainers_coll.replace_one({"_id": trainer["_id"]}, trainer)
    return result.modified_count > 0


def update_trainer_team(user_id: int, team: list) -> bool:
    """
    Updates the trainer's team.
    """
    result = trainers_coll.update_one(
        {"user_id": user_id},
        {"$set": {"team": team}}
    )
    return result.modified_count > 0


def update_trainer_money(user_id: int, amount: int) -> bool:
    """
    Updates the trainer's money. If the trainer doesn't have a money field, it is initialized.
    """
    result = trainers_coll.update_one(
        {"user_id": user_id},
        {"$set": {"money": amount}}
    )
    return result.modified_count > 0


def update_trainer_inventory(user_id: int, item: dict) -> bool:
    """
    Updates the trainer's inventory. If the inventory does not exist, it is created.
    """
    result = trainers_coll.update_one(
        {"user_id": user_id},
        {"$push": {"inventory": item}},  # Adds item to inventory array
        upsert=True  # Creates the inventory field if it doesn't exist
    )
    return result.modified_count > 0

def update_trainer_location(user_id:int, location):

    result = trainers_coll.update_one(
        {"user_id": user_id},
        {"$set": {"position": location}}
    )
    return result.modified_count > 0
