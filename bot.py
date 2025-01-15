import discord
import os # default module
from dotenv import load_dotenv

load_dotenv() # load all the variables from the env file
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

cogs_list = [
    'player-commands',
]

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')


@bot.slash_command(name="ping", description="Ping the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Ready to Catch them all?!")

from "mongodb/start" import create_or_get_trainer, create_pokemon_for_trainer, update_trainer_team

class StarterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Kein automatisches Timeout

    @discord.ui.button(label="Bulbasaur", style=discord.ButtonStyle.success)
    async def bulbasaur_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Du hast **Bulbasaur** gewählt!",
            ephemeral=True  # Nur für den klickenden User sichtbar
        )

    @discord.ui.button(label="Charmander", style=discord.ButtonStyle.danger)
    async def charmander_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Du hast **Charmander** gewählt!",
            ephemeral=True
        )

    @discord.ui.button(label="Squirtle", style=discord.ButtonStyle.primary)
    async def squirtle_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Du hast **Squirtle** gewählt!",
            ephemeral=True
        )
    async def handle_starter_choice(self, interaction: discord.Interaction, pokemon_name: str):
        """
        Sobald ein User auf einen Starter-Button klickt:
        1) Trainer in DB erstellen/holen.
        2) Pokémon in DB erstellen.
        3) Pokémon-ID ins Trainer-Dokument pushen.
        4) Bestätigung an den User senden.
        """
        user_id = interaction.user.id

        # 1) Trainer-Datensatz holen/erstellen
        trainer = create_or_get_trainer(user_id)

        # 2) Pokémon für den Trainer erstellen
        pokemon_id = create_pokemon_for_trainer(user_id, pokemon_name)

        # 3) Pokémon dem Team hinzufügen
        update_trainer_team(trainer["_id"], pokemon_id)

        # 4) Nachricht an den User
        await interaction.response.send_message(
            f"**{pokemon_name}**, the chosen one, appears in front of you. "
            "It's time to look around and investigate the area!\n"
            "_(Dein Trainer- und Pokémon-Datensatz wurde in der Datenbank angelegt.)_",
            ephemeral=True
        )



@bot.slash_command(name="start", description="Start your Pokemon Trainer Journey!")
async def start(ctx: discord.ApplicationContext):
    embed = discord.Embed(
            title="Willkommen in Zelquora!",
            description=(
                "Du wachst an einem Strand auf. Dein Kopf schmerzt, weil "
                "du auf einen Stein gefallen bist. Deine Erinnerungen sind "
                "verschwommen, du kennst nur noch deinen Namen und dein Geschlecht.\n\n"
                "Um dich herum findest du eine kleine Pokéball-Kapsel. "
                "Du wirfst sie in die Luft und ein Pokémon erscheint! "
                "Was für ein Pokémon siehst du vor dir?"
            ),
            color=discord.Color.gold()
        )

    # 2) View mit Buttons erstellen
    view = StarterView()

    # 3) Nachricht mit Embed und Buttons senden
    await ctx.respond(embed=embed, view=view)



bot.run(os.getenv('TOKEN')) # run the bot with the token