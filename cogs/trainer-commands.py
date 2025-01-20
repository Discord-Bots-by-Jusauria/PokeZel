import discord
from discord.ext import commands

# Falls du fetch_profile_data nutzt, importiere es hier.
from bot_util import make_embed
from mongodb.pokemon import registeres_pokedex_pokemon_name
from mongodb.trainer import get_trainer_with_team
from pojos.emoji_handle import app_emojis, get_emoji
from services.trainerUtilities import show_profile

subgroup = "trainer_"

class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
   
    @discord.slash_command(name=subgroup+"profile",description="Shows trainer profile")
    async def profile(self, ctx: discord.ApplicationContext):
        user_id = ctx.author.id
        await ctx.defer()  # oder direkt respond
        await show_profile(ctx, user_id)

    @discord.slash_command(name=subgroup+"dex",description="Your personal Pokedex")
    async def dex(self, ctx: discord.ApplicationContext):
        embed=make_embed("Your Pokedex - Zelquora","")
        registered=registeres_pokedex_pokemon_name(ctx.author.id)

        for available_pokemon in app_emojis:
            pokemon_registered = "❌ not registered"
            if available_pokemon in registered:
                pokemon_registered = "✅ registered"
            embed.add_field(name=f"{get_emoji(name=available_pokemon)} {available_pokemon}",value=pokemon_registered,inline=True)
        await ctx.respond(embed=embed)
        
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
