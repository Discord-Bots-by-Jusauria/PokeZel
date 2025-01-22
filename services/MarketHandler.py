import json
import os

from discord import Embed

from bot_util import make_embed
from pojos.emoji_handle import get_item_emoji
from services.AzurquoraHandler import AzurquoraHandler
from services.pokemon_api import get_itemPrice

class MarketHandler:
    #listType has to be the same name as Market_offers: specific list 
    @staticmethod
    async def addList(embed:Embed, listType, placeHandler: AzurquoraHandler):
        json_data = await placeHandler.load_story_data()
        listItems = json_data["market_offers"][listType]

        for item in listItems:
            if item.get("handler"):
                itemDetails ={
                    "cost": 1000
                }
            else:
                itemDetails = get_itemPrice(item["value"])
            embed.add_field(name=f"{get_item_emoji(item["value"])} {item["label"]} ${itemDetails["cost"]}", value=item["description"],inline=False)
    