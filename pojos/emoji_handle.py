# emoji_manager.py

# Dictionary to store emoji name-ID mappings
app_emojis = {
    "bulbasaur": 1329831574174437490,
    "charmander":1329853063422283867,
    "squirtle":1329853079843242004,
}
def get_emoji(name: str) -> str:

    emoji_id = app_emojis.get(name)
    if emoji_id:
        return f"<:{name}:{emoji_id}>"
    else:
        return None

item_emojis = {
    
}
def get_item_emoji(name:str):
    emoji_id = item_emojis.get(name)
    if emoji_id:
        return f"<:{name}:{emoji_id}>"
    else:
        return None