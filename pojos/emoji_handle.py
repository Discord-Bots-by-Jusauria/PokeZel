# emoji_manager.py

# Dictionary to store emoji name-ID mappings
app_emojis = {
    "Bulbasaur": 1329831574174437490,
}

def get_emoji(name: str) -> str:

    emoji_id = app_emojis.get(name)
    if emoji_id:
        return f"<:{name}:{emoji_id}>"
    else:
        return None
