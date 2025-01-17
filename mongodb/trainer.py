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
        pokemon_id = team_entry.get("pokemon_id")
        if pokemon_id:
            pokemon = pokemons_coll.find_one({"_id": ObjectId(pokemon_id)})
            if pokemon:
                for poke in pokemon.get("pokemons_owned", []):
                    team_with_details.append({
                        "nickname": poke.get("nickname"),
                        "lvl": poke.get("lvl"),
                        "name":poke.get("name")
                    })

    # Add detailed team to the trainer object
    trainer["team"] = team_with_details
    return trainer
