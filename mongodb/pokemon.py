from pymongo import MongoClient
from bson.objectid import ObjectId
# Stelle sicher, dass du hier deinen Connection-String einträgst
client = MongoClient("mongodb+srv://mewtumew1:hoihoihoi@cluster0.jpxvquh.mongodb.net/test")
db = client["PokeZel"]  # Beispiel: Datenbankname

pokemons_coll = db["pokemons"]   # Collection für Pokémon

def registered_pokedex_pokemon_names(user_id: int):
    # Find the document for the given user_id
    user_pokemon = pokemons_coll.find_one({"user_id": user_id})

    if not user_pokemon:
        return []  # Return an empty list if no Pokémon found for the user

    # Initialize a list to hold all evolution histories of Pokémon that were in the team
    raw_pokemon_names = []

    # Iterate through the pokemons_owned array and check for "was_in_team"
    for pokemon in user_pokemon["pokemons_owned"]:
        if pokemon.get("was_in_team", False):  # Ensure "was_in_team" exists and is True
            # Add the current Pokémon name
            raw_pokemon_names.append(pokemon["name"])

            # Add the evolution history names, if they exist
            if "evolution_history" in pokemon:
                raw_pokemon_names.extend(pokemon["evolution_history"])

    unique_pokemon_names = list(set(raw_pokemon_names))

    return  unique_pokemon_names  
    
