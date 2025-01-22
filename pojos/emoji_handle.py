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
    "potion":1331585763048947712,
    "super-potion":1331587431362990124,
    "fresh-water":1331587429651714100,
    "soda-pop":1331587422730981376,
    "lemonade":1331587421049192490,
    "antidote":1331587418834468926,
    "burn-heal":1331587414900211784,
    "ice-heal":1331587413017100290,
    "paralyze-heal":1331587411729322037,
    "awakening":1331587410190143500,
    "water-stone":1331587560882966590,
    "fire-stone":1331587559889047604,
    "thunder-stone":1331587558227836929,
    "leaf-stone":1331587556801908837,
    "poke-ball":1331587555497345086,
    "great-ball":1331587554113224704,
    "safari-ball":1331587552356077668,
    "surf":1331587483862831136,
}
def get_item_emoji(name:str):
    emoji_id = item_emojis.get(name)
    
    nameSend = name.lower().replace("-", "")
    if emoji_id:
        return f"<:{nameSend}:{emoji_id}>"
    else:
        return None