from decimal import setcontext
from email import message
import json
import random
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

def load_items(filename):
    with open("pojos/json/"+filename, "r", encoding="utf-8") as file:
        return json.load(file)
    
def get_messages(section, petname, sick=""):
    messages = load_items("messages.json")
    messages= messages[section]["messages"]
    message= random.choice(messages)
    return message.format(pet_name = petname, sickness = sick)
def get_messages_mood(section, petname, mood, sick=""):
    messages = load_items("messages.json")
    messages= messages[section][mood]["messages"]
    message= random.choice(messages)
    return message.format(pet_name = petname, sickness = sick)
def get_sleep_messages(petname, mood):
    messages = load_items("events.json")
    messages= messages["sleeping"][mood]
    messageList = []
    for message in messages:
        message["message"]=message["message"].format(pet_name = petname)
        messageList.append(message)
    return random.choice(messageList)
    
def get_attention_messages(action,species, petname, mood):
    messages = load_items("events.json")
    messages= messages["attention"][action][species][mood]
    messageList = []
    for message in messages:
        message["message"]=message["message"].format(pet_name = petname)
        messageList.append(message)
    return messageList