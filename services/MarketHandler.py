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
    async def getMarketOffers(listType, placeHandler: AzurquoraHandler):
        json_data = await placeHandler.load_story_data()
        listItems = json_data["market_offers"][listType]
        newList = []
        for item in listItems:
            itemCost = 0
            if item.get("handler"):
                itemCost ={
                    "cost": 1000
                }
            else:
                itemCost = get_itemPrice(item["value"])["cost"]
            newList.append({"value":item["value"],"label":item["label"], "description":item["description"], "cost" :itemCost})
        return newList
    @staticmethod
    async def addList(embed:Embed, listType, placeHandler: AzurquoraHandler):
            list = await MarketHandler.getMarketOffers(listType,placeHandler)
            for item in list:
                embed.add_field(name=f"{get_item_emoji(item["value"])} {item["label"]} ${item["cost"]}", value=item["description"],inline=False)
    