import discord

def make_embed(title: str, description: str) -> discord.Embed:
    """
    Creates and returns a discord.Embed with the given parameters.
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.DarkVividPink()
    )
    return embed
