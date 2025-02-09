import json
import discord
import os  # default module
from dotenv import load_dotenv
from bot_util import make_embed


from services.handlerList import ALL_HANDLERS
from mongodb.owner import get_owner, create_adoption
load_dotenv()  # load all the variables from the .env file
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


# List of cogs to load (e.g., "player-commands")
cogs_list = [
    'owner-commands',
]

# Load all cogs from the list
for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')


def load_pets():
    with open("./pojos/pets_basic.json", "r", encoding="utf-8") as file:
        return json.load(file)

pets_data = load_pets()
class AdoptDropdown(discord.ui.Select):
    def __init__(self, user_id: int):
        self.user_id = user_id  # Store user ID to prevent others from selecting
        
        options = [
            discord.SelectOption(label=pet["species"], description=f"Evolves into: {', '.join(pet['evolution'])}")
            for pet in pets_data
        ]
        super().__init__(placeholder="Choose your pet!", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This menu isn't for you!", ephemeral=True)
            return
        
        selected_pet = next((p for p in pets_data if p["species"] == self.values[0]), None)
        if not selected_pet:
            await interaction.response.send_message("Pet not found!", ephemeral=True)
            return
        
        create_adoption(interaction.user,selected_pet)
        await interaction.response.send_message(embed=make_embed("Adopted!", f"You adopted a **{selected_pet['species']}** 🎉"))

class AdoptView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=60)
        self.add_item(AdoptDropdown(user_id))


@bot.slash_command(name="adopt", description="Get your own Server Pet :D")
async def adopt(interaction: discord.Interaction):
    user = get_owner(interaction.user.id)
    if user:
        await interaction.response.send_message(embed=make_embed("You already have a pet!", "You can't adopt another one."), ephemeral=True)
        return
    embed = make_embed("Adopt a Pet!", "Choose one of the available pets from the dropdown below.")
    for pet in pets_data:
        evolution = ", ".join(pet["evolution"])  # Join evolution types with commas
        
        # Add a field for each pet
        embed.add_field(
            name=f"{pet["species"]}",
            value=f"Type: {pet["type"]} -- Evolutions: {evolution}",
            inline=False
        )
    await interaction.response.send_message(embed=embed, view=AdoptView(interaction.user.id))


# Finally, run the bot with the token from .env
bot.run(os.getenv('TOKEN'))
