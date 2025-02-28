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
    if (pet.get("sick") or {}).get("name")== "Overstimulated":
        await ctx.response.send_message(embed=make_embed("Curled up", "Everything seems too much for your little pet. Making it hard for it. Leave it be for a while until its calmed."), ephemeral=True)
        return False
    return True

async def isPetStatsFine(pet):
    sicknesses = load_items("sickness.json")
    reasons={"status": 10, "reasons": []}
    if pet["happiness"]>100:
        sickness = [s for s in sicknesses if s["name"] == "Overstimulated"][0]
        if random.randint(0,100)<sickness["triggers"]["chance"]:
            pet["sick"] = sickness
            if not pet["logs"]["sick"]:
                pet["logs"]["sick"] = {"timestamp":0,"range":[0,0]}
            pet["logs"]["sick"]["timestamp"] = int(datetime.now().timestamp())
            pet["logs"]["sick"]["range"] = sickness["range"][0]
        reasons["status"] =0
        reasons["reasons"].append("happiness")
    if pet["hunger"]>100 or pet["thirst"]>100: 
        sickness = [s for s in sicknesses if s["name"] == "Nausea"][0]
        if random.randint(0,100)<sickness["triggers"]["chance"]:
            pet["sick"] = sickness
            if not pet["logs"]["sick"]:
                pet["logs"]["sick"] = {"timestamp":0,"range":[0,0]}
            pet["logs"]["sick"]["timestamp"] = int(datetime.now().timestamp())
            pet["logs"]["sick"]["range"] = sickness["range"][0]
        reasons["status"] =0
        reasons["reasons"].append("food")
    
    pet["happiness"] = max(0,min(100,pet["happiness"]))
    pet["thirst"] = max(0,min(100,pet["thirst"]))
    pet["hunger"] = max(0,min(100,pet["hunger"]))
    pet["health"] = max(0,min(100,pet["health"]))
    pet["energy"] = max(0,min(100,pet["energy"]))
    
    return reasons