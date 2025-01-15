import discord
from discord.ext import commands

class Player(commands.Cog):
  def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot

  @commands.command()
  async def profile(description="Player profile",):
    async def profile(self, ctx: discord.ApplicationContext):
          # 1) Nutzerdaten holen (anhand Discord-User-ID)
          user_id = ctx.author.id
          data = fetch_profile_data(user_id)

          # 2) Prüfen, ob Daten vorhanden sind
          if not data:
              await ctx.respond("Keine Profildaten gefunden!")
              return

          # 3) Embed erstellen
          embed = discord.Embed(
              title=f"{data['name']}'s Profile",
              description="Hier siehst du deine aktuellen Spiel-Daten",
              color=0x00FF00
          )

          # 4) Thumbnail: Aktuelles Profilbild des Users
          if ctx.author.avatar:
              embed.set_thumbnail(url=ctx.author.avatar.url)
          else:
              embed.set_thumbnail(url=ctx.author.default_avatar.url)

          # 5) Felder hinzufügen
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

          # 6) Antwort senden
          await ctx.respond(embed=embed)

  @commands.command()
  async def dex(ctx, num1: int, num2: int):
    sum = num1 - num2
    await ctx.respond(f"{num1} minus {num2} is {sum}.")

  @commands.command()
  async def craft(ctx, num1: int, num2: int):
    sum = num1 - num2
    await ctx.respond(f"{num1} minus {num2} is {sum}.")

  @commands.command()
  async def news(ctx, num1: int, num2: int):
    sum = num1 - num2
    await ctx.respond(f"{num1} minus {num2} is {sum}.")

  @commands.command()
  async def team(ctx, num1: int, num2: int):
    sum = num1 - num2
    await ctx.respond(f"{num1} minus {num2} is {sum}.")

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Player(bot)) # add the cog to the bot