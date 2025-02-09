import json
import os

from discord import Embed

from bot_util import make_embed
from pojos.emoji_handle import get_item_emoji

class MarketHandler:
    @staticmethod
    async def handle_action(action_name: str, *args, **kwargs):
        print("rawt")