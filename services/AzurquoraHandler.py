import json
import os

from bot_util import make_embed
from mongodb.start import create_starter_pokemon_for_trainer, update_trainer_team
from mongodb.trainer import get_trainer_with_team

class AzurquoraHandler:
    async def load_story_data():
        file_path = os.path.join("locations","cities", "azurquora.json")

        # Open and read the JSON file
        with open(file_path, "r", encoding="utf-8") as file:
            story_data = json.load(file)  # Returns a dictionary
            return story_data  # No .json call here


    @staticmethod
    async def handle_action(action_name: str, *args, **kwargs):
        actions = {
            "add_starter_pokemon": AzurquoraHandler.add_starter_pokemon,
            # Add more actions here as needed
        }
        action = actions.get(action_name)
        if action:
            return await action(*args, **kwargs)
        else:
            raise ValueError(f"Action '{action_name}' not found in AzurquoraHandler.")

    @staticmethod
    async def add_starter_pokemon(interaction, trainer_data, pokemon_name):
        create_starter_pokemon_for_trainer(trainer_data["user_id"], pokemon_name)
        update_trainer_team(trainer_data["user_id"], 1)
        trainer_data = get_trainer_with_team(trainer_data["user_id"])
        
