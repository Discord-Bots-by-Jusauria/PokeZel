import discord
from discord.ext import commands

# Falls du fetch_profile_data nutzt, importiere es hier.
# from .deine_db_datei import fetch_profile_data

class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="profile",
        description="Player profile"
    )
    async def profile(self, ctx: discord.ApplicationContext):
        # Hier kommt dein Code für den 'profile'-Slash-Command:
        user_id = ctx.author.id

        # Annahme: fetch_profile_data kommt aus deiner DB-Hilfsdatei
        data = fetch_profile_data(user_id)
        if not data:
            await ctx.respond("Keine Profildaten gefunden!")
            return

        embed = discord.Embed(
            title=f"{data['name']}'s Profile",
            description="Hier siehst du deine aktuellen Spiel-Daten",
            color=0x00FF00
        )

        # Thumbnail
        if ctx.author.avatar:
            embed.set_thumbnail(url=ctx.author.avatar.url)
        else:
            embed.set_thumbnail(url=ctx.author.default_avatar.url)

        # Felder befüllen
        embed.add_field(name="Dollar", value=data["dollar"], inline=False)
        embed.add_field(name="Game gestartet am", value=data["started_game"], inline=False)
        embed.add_field(name="Rolle", value=data["role"], inline=False)
        embed.add_field(name="Dex gefüllt", value=data["dex_filled"], inline=False)
        embed.add_field(name="Shiny Count", value=data["shiny_count"], inline=False)
        embed.add_field(name="Favorit", value=data["favorite_pokemon"], inline=False)
        embed.add_field(name="Passives Training", value=str(data["passive_training"]), inline=False)
        embed.add_field(name="Team", value=", ".join(data["team"]) if data["team"] else "Kein Team", inline=False)
        embed.add_field(name="Badges", value=data["badges"], inline=False)
        embed.add_field(name="Trainer-Level", value=data["trainer_level"], inline=False)

        await ctx.respond(embed=embed)

    @discord.slash_command(
        name="dex",
        description="Testkommandos Dex"
    )
    async def dex(self, ctx: discord.ApplicationContext, num1: int, num2: int):
        result = num1 - num2
        await ctx.respond(f"{num1} minus {num2} ist {result}.")

    @discord.slash_command(
        name="craft",
        description="Testkommandos Craft"
    )
    async def craft(self, ctx: discord.ApplicationContext, num1: int, num2: int):
        result = num1 - num2
        await ctx.respond(f"{num1} minus {num2} ist {result}.")

    @discord.slash_command(
        name="news",
        description="Testkommandos News"
    )
    async def news(self, ctx: discord.ApplicationContext, num1: int, num2: int):
        result = num1 - num2
        await ctx.respond(f"{num1} minus {num2} ist {result}.")

    @discord.slash_command(
        name="team",
        description="Testkommandos Team"
    )
    async def team(self, ctx: discord.ApplicationContext, num1: int, num2: int):
        result = num1 - num2
        await ctx.respond(f"{num1} minus {num2} ist {result}.")


def setup(bot):
    bot.add_cog(Player(bot))
