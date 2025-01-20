import json
import os

from bot_util import make_embed
from mongodb.start import create_starter_pokemon_for_trainer, update_trainer_team
from mongodb.trainer import get_trainer_with_team
from services.trainerUtilities import show_profile

class TrainerHandler:
    @staticmethod
    async def handle_action(action_name: str, *args, **kwargs):
        actions = {
            "call_profile": TrainerHandler.call_profile,
            # Add more actions here as needed
        }
        action = actions.get(action_name)
        if action:
            return await action(*args, **kwargs)
        else:
            raise ValueError(f"Action '{action_name}' not found in TrainerHandler.")

    @staticmethod
    async def call_profile(interaction, trainer_data, *args, **kwargs):
        user_id = trainer_data["user_id"]
        
        # Achtung: Möglicherweise musst du hier interaction defer-en,
        # wenn du das nicht schon getan hast
        if not interaction.response.is_done():
            await interaction.response.defer()
        
        await show_profile(interaction, user_id)
        
