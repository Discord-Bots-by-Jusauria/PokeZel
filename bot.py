import discord
import os  # default module
from dotenv import load_dotenv

load_dotenv()  # load all the variables from the .env file
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

# List of cogs to load (e.g., "player-commands")
cogs_list = [
    'player-commands',
]

# Load all cogs from the list
for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')

# Import the MongoDB helper functions
from mongodb.start import create_or_get_trainer, create_pokemon_for_trainer, update_trainer_team


class StarterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # No automatic timeout

    @discord.ui.button(label="Bulbasaur", style=discord.ButtonStyle.success)
    async def bulbasaur_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # The simplest approach: show a quick confirmation
        # If you want full trainer creation logic, call handle_starter_choice below.
        # Just replace "Bulbasaur" and "You have chosen Bulbasaur!" as needed.
        await self.handle_starter_choice(interaction, "Bulbasaur")

    @discord.ui.button(label="Charmander", style=discord.ButtonStyle.danger)
    async def charmander_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_starter_choice(interaction, "Charmander")

    @discord.ui.button(label="Squirtle", style=discord.ButtonStyle.primary)
    async def squirtle_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_starter_choice(interaction, "Squirtle")

    async def handle_starter_choice(self, interaction: discord.Interaction, pokemon_name: str):
        """
        Once a user clicks on a starter button:
         1) Fetch/create trainer data in MongoDB.
         2) Create a Pokémon document in MongoDB.
         3) Add the Pokémon's ID to the trainer's 'team'.
         4) Send a confirmation message to the user.
        """
        user_id = interaction.user.id

        # 1) Fetch or create the trainer document
        trainer = create_or_get_trainer(user_id)

        # 2) Create the Pokémon document for this trainer
        pokemon_id = create_pokemon_for_trainer(user_id, pokemon_name)

        # 3) Push the Pokémon ID into the trainer's team array
        update_trainer_team(trainer["_id"], pokemon_id)

        # 4) Reply to the user
        await interaction.response.send_message(
            f"**{pokemon_name}**, the chosen one, appears in front of you.\n"
            "It's time to look around and investigate the area!\n"
            "_(Your trainer and Pokémon records have been created in the database.)_",
            ephemeral=True
        )


@bot.slash_command(name="start", description="Start your Pokémon Trainer Journey!")
async def start(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title="Welcome to Zelquora!",
        description=(
            "You wake up on a beach, your head hurting from hitting a rock. "
            "Your memories are hazy; you only remember your name and your gender.\n\n"
            "Looking around, you find a small Poké Ball. You toss it into the air, and a Pokémon appears! "
            "Which Pokémon do you see in front of you?"
        ),
        color=discord.Color.gold()
    )

    # 2) Create the view containing the buttons
    view = StarterView()

    # 3) Send the message with the embed and buttons
    await ctx.respond(embed=embed, view=view)


# Finally, run the bot with the token from .env
bot.run(os.getenv('TOKEN'))
