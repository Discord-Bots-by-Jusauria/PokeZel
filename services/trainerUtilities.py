import discord
from discord.ext import commands

from bot_util import make_embed
from mongodb.trainer import get_trainer_with_team
from pojos.emoji_handle import get_emoji

async def show_profile(interaction: discord.Interaction, user_id: int):

    # Annahme: fetch_profile_data kommt aus deiner DB-Hilfsdatei
    data = get_trainer_with_team(user_id)
    if not data:
        await interaction.followup.send(embed=make_embed("No Trainer Found"))
        return

    embed = make_embed(
        title=data['name'],description=""
    )

    # Thumbnail
    if interaction.user.avatar:
        embed.set_thumbnail(url= interaction.user.avatar.url)
    else:
        embed.set_thumbnail(url= interaction.user.default_avatar.url)

    # Felder befüllen
    embed.add_field(name="Trainer-Level", value=data["trainer_lvl"], inline=True)
    embed.add_field(name="Role", value=data["role"], inline=True)

    embed.add_field(name="PokeDollar", value=data["dollar"], inline=True)
    embed.add_field(name="Favorite", value=data["fav"], inline=False)

    embed.add_field(name="Dex filled", value=0, inline=True)
    embed.add_field(name=":sparkles: Shiny", value=data["shiny_count"], inline=True)
    
    stringTeam = ""
    for pokemon in data["team"]:
        shiny_star = ":sparkles:" if pokemon["is_shiny"] else ""
        stringTeam += f"lvl {pokemon['lvl']} {get_emoji(pokemon['name'])} {shiny_star} {pokemon['nickname']}\n"
    embed.add_field(name="Team", value=stringTeam, inline=False)
    embed.add_field(name="Passive training", value=str(data["passive"]), inline=False)

    embed.add_field(name="Badges", value=data["badges"], inline=False)
    embed.add_field(name="Started", value="<t:"+str(data["started"])+":F>", inline=False)
    

    await interaction.followup.send(embed=embed)