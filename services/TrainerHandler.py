import json
import os

from bot_util import make_embed
from mongodb.start import create_starter_pokemon_for_trainer, update_trainer_team
from mongodb.trainer import delete_trainer, get_trainer_with_team
from services.trainerUtilities import show_profile

class TrainerHandler:
    @staticmethod
    async def handle_action(action_name: str, *args, **kwargs):
        actions = {
            "call_profile": TrainerHandler.call_profile,
            "delete": TrainerHandler.delete,
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
    @staticmethod
    async def delete(interaction, trainer_data, *args, **kwargs):
        user_id = trainer_data["user_id"]
        
        if not interaction.response.is_done():
            await interaction.response.defer()
        
        dead= delete_trainer(user_id)
        if dead:
             await interaction.followup.send(embed=make_embed("You hit yourself","With a sharp stone you hit yourself. As you lie there in the sand you think about if it was worth it. Maybe next life, you get a shiny..."))
        else:
            await interaction.followup.send(embed=make_embed("You tried","With a sharp stone you tried to hit yoursel. The stone missed your head and bounced on the wall. Shattering in millions of pieces. Guess it's not your time yet."))
        
