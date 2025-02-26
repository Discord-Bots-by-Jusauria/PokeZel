from datetime import date, datetime, timedelta
import random
from turtle import update
import discord
from discord.ext import commands, tasks

# Falls du fetch_profile_data nutzt, importiere es hier.
from bot_util import load_items, make_embed, get_messages, get_messages_mood
from utilities.profile import show_pet_profile
from mongodb.owner import get_all_owner, get_owner
from mongodb.pet import nicknamePet, update_pet
from utilities.pet_interaction import drinkView, feedView

async def isAOwner(user_id,ctx):
    user_data = get_owner(user_id=user_id)
    if not user_data:
        await ctx.response.send_message(embed=make_embed("You are not a Pet Owner"), ephemeral=True)
        return False
    return user_data

async def isPetWorkable(pet,ctx):
    if pet["died"]:
        await ctx.response.send_message(embed=make_embed("It's a corpse... you can't do anythign now."), ephemeral=True)
        return False
    if pet["is_sleeping"]:
        await ctx.response.send_message(embed=make_embed("Your pet is asleep. Until you wake up you can't do anything with it."), ephemeral=True)
        return False
    return True

