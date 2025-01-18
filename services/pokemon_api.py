import requests
BASE_URL = "https://pokeapi.co/api/v2"

def get_pokemon(pokemon_name: str) -> dict:
    url = f"{BASE_URL}/pokemon/{pokemon_name.lower()}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"Pokémon '{pokemon_name}' not found. Status code: {response.status_code}")

def get_gender(pokemon_name: str) -> dict:
    urlFemale = f"{BASE_URL}/gender/1"  # "1" corresponds to the female list in PokeAPI
    urlMale = f"{BASE_URL}/gender/2" 
    responseFemale = requests.get(urlFemale)
    responseMale = requests.get(urlMale)

    
    if responseFemale.status_code == 200 and responseMale.status_code == 200:
        # Parse the JSON response
        dataFemale = responseFemale.json()
        dataMale = responseMale.json()
        
        # Search for the Pokémon in the female list
        for entryf in dataFemale.get("pokemon_species_details", []):
            if entryf["pokemon_species"]["name"] == pokemon_name.lower():
                for entrym in dataMale.get("pokemon_species_details", []):
                        if entrym["pokemon_species"]["name"] == pokemon_name.lower():
                            # Get the rate from the female list
                            female_rate = entryf["rate"]
                            male_rate = entrym["rate"]
                            return {"male_rate": male_rate, "female_rate": female_rate}
        # If Pokémon is not found in the list, it's genderless
        return {"male_rate": -1, "female_rate": -1}
    else:
        # Handle cases where the API fails
        raise ValueError(f"Failed to fetch gender data. Status code: {response.status_code}")


def get_ability(ability_name: str) -> dict:
    url = f"{BASE_URL}/ability/{ability_name.lower()}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"Ability '{ability_name}' not found. Status code: {response.status_code}")

def get_type(type_name: str) -> dict:
    url = f"{BASE_URL}/type/{type_name.lower()}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"Type '{type_name}' not found. Status code: {response.status_code}")

def get_nature(elementNumber: int) -> dict:
    url = f"{BASE_URL}/nature/"
    responseName = requests.get(url)
    nature_details = requests.get(f"{url}/{elementNumber}")
    
    if responseName.status_code == 200 and nature_details.status_code==200:
        return {
            "name": responseName.json()["results"][elementNumber-1]["name"],
            "decreased_stat": nature_details.json()["decreased_stat"]["name"] if nature_details.json()["decreased_stat"] else None,
            "hates_flavor": nature_details.json()["hates_flavor"]["name"] if nature_details.json()["hates_flavor"] else None,
            "increased_stat": nature_details.json()["increased_stat"]["name"] if nature_details.json()["increased_stat"] else None,
            "likes_flavor":  nature_details.json()["likes_flavor"]["name"] if nature_details.json()["likes_flavor"] else None
        }
    else:
        raise ValueError(f"Type '{type_name}' not found. Status code: {response.status_code}")

def get_growrate(name:str,lvl:int,listStart=1):
    url = f"{BASE_URL}/growth-rate/{listStart}"
    response = requests.get(url)    
    if response.status_code == 200:
        for pokemon in response.json()["pokemon_species"]:
            if pokemon["name"] == str.lower(name):
                return {
                    "grow_name":response.json()["name"],
                    "id": response.json()["id"],
                    "next_lvl_exp": response.json()["levels"][lvl]["experience"]
                }
        return get_growrate(name=name,lvl=lvl,listStart=listStart+1)

   