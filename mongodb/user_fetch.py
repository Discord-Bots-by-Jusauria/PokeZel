from pymongo import MongoClient

def fetch_profile_data(user_id: int):
        # Hier deine Verbindung zu MongoDB herstellen (Connection String, DB-Namen usw.)
    client = MongoClient("mongodb+srv://mewtumew1:hoihoihoi@cluster0.jpxvquh.mongodb.net/test")
    db = client["PokeZel"]  # Beispiel: Datenbankname

    collection = db["trainers"]   # Collection für Spieler/Trainer

    # Ein Dokument anhand der user_id finden
    user_data = collection.find_one({"user_id": user_id})
    if not user_data:
        return None  # Falls nichts gefunden wird
    if user_data["team"]:
        user_data["team"] = ", ".join(str(member_id) for member_id in user_data["team"])
    else:
        user_data["team"] = 'Kein Team'

    # Rückgabe als Dictionary
    return {
        "name": user_data.get("name", "Unknown"),
        "dollar": user_data.get("dollar", 0),
        "started_game": user_data.get("started_game", "N/A"),
        "role": user_data.get("role", "N/A"),
        "dex_filled": user_data.get("dex_filled", 0),
        "shiny_count": user_data.get("shiny_count", 0),
        "favorite_pokemon": user_data.get("favorite_pokemon", "N/A"),
        "passive_training": user_data.get("passive_training", False),
        "team": user_data.get("team", []),
        "badges": user_data.get("badges", 0),
        "trainer_level": user_data.get("trainer_level", 1),
    }
