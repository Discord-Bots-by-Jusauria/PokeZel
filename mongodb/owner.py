from datetime import datetime, timedelta
import time
import random
from pymongo import MongoClient
from bson.objectid import ObjectId
# Stelle sicher, dass du hier deinen Connection-String einträgst
client = MongoClient("mongodb+srv://mewtumew1:hoihoihoi@cluster0.jpxvquh.mongodb.net/test")
db = client["Pointlink"]  # Beispiel: Datenbankname
owner_coll = db["owner"]   # Collection für Spieler/Owner
dbg = client["General"]
people_coll = dbg["people"]

def get_owner(user_id: int) -> dict:
    # Fetch the owner document
    owner = owner_coll.find_one({"user_id": user_id})
    if not owner:
        return None  # Owner not found
    
    return owner

def create_adoption(user: any, selectedPet: any) -> bool:
    peep = people_coll.find_one({"user":str(user.id)})
    money = 10
    if peep:
        money = peep["points"]
    #random values set of pet
    print(selectedPet["happiness"][0])
    pet = selectedPet
    pet["happiness"]= random.randint(selectedPet["happiness"][0], selectedPet["happiness"][1])
    pet["intelligence"]= random.randint(selectedPet["intelligence"][0], selectedPet["intelligence"][1])
    pet["hunger"]= random.randint(selectedPet["hunger"][0], selectedPet["hunger"][1])
    pet["thurst"]= random.randint(selectedPet["thurst"][0], selectedPet["thurst"][1])
    pet["trust"]= random.randint(selectedPet["trust"][0], selectedPet["trust"][1]) 

    # New document to insert into MongoDB
    new_entry = {
        "user_id": user.id,
        "user_name": user.name,
        "points": money,
        "start_of_game": int( datetime.now().timestamp()),
        "rank": 0,
        "check-in":  int((datetime.now() - timedelta(days=1)).timestamp()),
        "commission_target":{
            "name":"none",
            "amount":0,
            "goal":0
            } ,
        "pet_slot_available": 1,
        "daily_task": "",
        "inventory": [],
        "pet": [pet]
    }

    try:
        # Insert the new entry into the 'owner' collection
        owner_coll.insert_one(new_entry)
        return True  # Return True on success
    except Exception as e:
        print(f"Error inserting adoption: {e}")
        return False  # Return False if something went wrong

## Updates

def updateCheckin(user_id:int,amount:int):
    result = owner_coll.update_one({"user_id": user_id}, {"$inc": {"points": amount},"$set":{"check-in":int(datetime.now().timestamp())}})
    
    return result.modified_count > 0

def updateBday(user_id:int,birthday:str):
    month, day = map(int, birthday.split("-"))
    current_year = datetime.now().year

    # Convert to datetime for this year
    bday_this_year = datetime(year=current_year, month=month, day=day)

    # If the birthday already passed this year, use next year
    if bday_this_year < datetime.now():
        bday_this_year = bday_this_year.replace(year=current_year + 1)

    # Convert to timestamp
    timestamp = int(time.mktime(bday_this_year.timetuple()))
    result = owner_coll.update_one({"user_id": user_id}, {"$set": {"bday": timestamp}})
    if result ==0:
        return;
    return timestamp;

    