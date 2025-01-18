from pymongo import MongoClient
from bson.objectid import ObjectId
from services.pokemon_api import get_growrate, get_nature, get_pokemon, get_gender
import random

client = MongoClient("mongodb+srv://mewtumew1:hoihoihoi@cluster0.jpxvquh.mongodb.net/test")
db = client["PokeZel"]  
pokemons_coll = db["pokemons"] 


def create_new_Pokemon(name:str, lvl: int,team_requirements=None):
    # basic pokemon stuff
    pokemon_info = get_pokemon(name)
    if pokemon_info:
        # gender - ? / 8 - if -1 its genderless
        gender = "Female"
        pokemon_genderrate = get_gender(name)
        if pokemon_genderrate["female_rate"] >0 :
            rate = pokemon_genderrate["female_rate"]+ pokemon_genderrate["male_rate"]
            genderChance=random.randint(1,rate)
            if pokemon_genderrate["male_rate"] >= pokemon_genderrate["female_rate"]:
                if genderChance <= pokemon_genderrate["male_rate"]:
                    gender = "Male"
            else:
                 if genderChance > pokemon_genderrate["female_rate"]:
                      gender = "Male"
        else:
            gender= "None"
        # Ability
        normalAbility = []
        hiddenAbility = ""
        abilityAsigned = ""
        for ability in pokemon_info["abilities"]:
            if ability["is_hidden"]:
                hiddenAbility = ability
            else:
                normalAbility.append(ability)
        
        hiddenChance = random.randint(0,100)
        if hiddenChance<6:
            abilityAsigned=hiddenChance
        else:
            abilityAsigned = normalAbility[random.randint(0,normalAbility.__len__()-1)]
        # Attack selection
        avaibleAttacks=[]
        useAttacks=[]
        for attack in pokemon_info["moves"]:
            if attack["version_group_details"][attack["version_group_details"].__len__()-1][ "move_learn_method"]["name"] == "level-up":
                if attack["version_group_details"][attack["version_group_details"].__len__()-1]["level_learned_at"] <=lvl:
                    avaibleAttacks.append({"name": attack["move"]["name"],"url":attack["move"]["url"]})

        if avaibleAttacks.__len__()>4:
            positions = random.sample(range(avaibleAttacks.__len__()), 4)
            useAttacks = [avaibleAttacks[i] for i in positions]
        else:
            useAttacks = avaibleAttacks

        # Trust and Happiness
        trust_base = 80
        happiness_base = 70
        min_trust = 10
        min_happiness = 5
        max_level = 100  # Assume maximum level is 100

        decay_rate_trust = (trust_base - min_trust) / max_level
        decay_rate_happy= (happiness_base - min_happiness) / max_level
        new_trust_state = trust_base - (decay_rate_trust * lvl)
        new_happy_state = happiness_base - (decay_rate_happy * lvl)

        #nature and stats
        nature = get_nature(random.randint(1,20))
        potential = random.randint(1,100)
        stats = []

        for stat in pokemon_info["stats"]:
           stats.append({"name":stat["stat"]["name"],"base_stat":stat["base_stat"],"value":0})
        calculate_pokemon_stats(all_Stats=stats,nature=nature,potential=potential,lvl=lvl)
        # grow Rate
        growRateAndNextLvl = get_growrate(pokemon_info["name"],lvl)
        #held item
        heldItem = None
        for item in pokemon_info["held_items"]:
            getItemChance = random.randint(1,100)
            if getItemChance <= item["version_details"][item["version_details"].__len__()-1]["rarity"] and heldItem==None:
                heldItem = {
                    "name": item["name"],
                    "url": item["url"]
                }
        
        return {
            "name": pokemon_info["name"],
            "nickname": pokemon_info["name"], 
            "types":[type["type"]["name"] for type in pokemon_info["types"]],
            "lvl": lvl,
            "gender": gender,
            "ability": abilityAsigned,
            "attacks": useAttacks,
            "trust_level": max(min_trust, int(new_trust_state)) ,
            "motivation": 0,
            "happiness": max(min_happiness, int(new_happy_state)) ,
            "nature": nature,
            "potential": potential,
            "stats": stats,
            "grow_rate":growRateAndNextLvl,
            "held_item": heldItem,
            "passive_training": False,
            "was_in_team": False,
            "team_requirement": team_requirements,
            "evolution_history":[
                pokemon_info["name"]
            ]
            }
        
def calculate_pokemon_stats(all_Stats,nature,potential,lvl):
    for stat in all_Stats:        
        nature_modifier = 1
        if nature['increased_stat'] == stat["name"]:
            nature_modifier = 1.1
        elif nature['decreased_stat'] == stat["name"]:
            nature_modifier = 0.9

        stat["value"] = round(((stat["base_stat"]*lvl/100)+5) * (1 + (potential / 100)) * nature_modifier)

def registeres_pokedex_pokemon_name(user_id: int):
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
    
