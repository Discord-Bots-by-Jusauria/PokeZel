import json
import discord

def make_embed(title: str, description="") -> discord.Embed:
    """
    Creates and returns a discord.Embed with the given parameters.
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.dark_blue()
    )
    return embed

def load_items(fileName):
    with open("pojos/"+fileName, "r") as file:
        return json.load(file)