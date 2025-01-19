import discord

def make_embed(title: str, description="") -> discord.Embed:
    """
    Creates and returns a discord.Embed with the given parameters.
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.dark_magenta()
    )
    return embed
