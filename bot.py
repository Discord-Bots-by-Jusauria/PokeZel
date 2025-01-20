import discord
import os  # default module
from dotenv import load_dotenv
from bot_util import make_embed

# MongoDB helper functions
from mongodb.pokemon import create_new_Pokemon
from mongodb.start import create_trainer, create_starter_pokemon_for_trainer, update_trainer_team
from mongodb.trainer import get_trainer_with_team, update_trainer_location
from services.TrainerHandler import TrainerHandler
from services.AzurquoraHandler import AzurquoraHandler

load_dotenv()  # load all the variables from the .env file
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


# List of cogs to load (e.g., "player-commands")
cogs_list = [
    'trainer-commands',
]

# Load all cogs from the list
for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')

ALL_HANDLERS  = {
    "azurquora": AzurquoraHandler,
     "trainer": TrainerHandler,
}

async def handle_action(interaction, trainer_data, action_name, handler_name=None, *args, **kwargs):
    """
    Dynamically calls the appropriate city handler for the given action.
    """
    if handler_name is None:
        # Fallback: city-Handler nehmen
        city = trainer_data["position"]["city"]
        handler_class = ALL_HANDLERS.get(city)
    else:
        # Spezifischen Handler (z.B. 'trainer')
        handler_class = ALL_HANDLERS.get(handler_name)

    if not handler_class:
        raise ValueError(f"No handler found for city '{city}'.")
    await handler_class.handle_action(action_name, interaction, trainer_data, *args, **kwargs)

async def handle_button_click(interaction: discord.Interaction):
    trainer_data = get_trainer_with_team(user_id= interaction.user.id)
    current_city = trainer_data["position"]["city"]
    current_location = trainer_data["position"]["location"]
    current_step = trainer_data["position"]["story_step"]

    # Get the current step details from the JSON
    story_json = await ALL_HANDLERS.get(current_city).load_story_data()
    location_data = story_json["locations"].get(current_location, [])
    step_data = next((step[current_step] for step in location_data if current_step in step), None)
    
    if not step_data:
        await interaction.response.send_message("Could not find the next story step.", ephemeral=True)
        return

    pokemon_name = trainer_data["team"][0]["name"].capitalize() if trainer_data.get("team") else "Pokémon"
    player_name = trainer_data["name"].capitalize()

    step_data["title"] = step_data["title"].replace("{pokemon_name}", pokemon_name).replace("{player_name}", player_name)
    step_data["description"] = step_data["description"].replace("{pokemon_name}", pokemon_name).replace("{player_name}", player_name)
    
    # Render the options
    view = discord.ui.View()
    for option in step_data["options"]:
        if "next" in option:
            custom_id = option["label"]+option["next"]["step"]
        else:
            custom_id = option["action"]
        button = discord.ui.Button(label=option["label"], custom_id=custom_id)
        
        # Attach a callback to handle the button click
        async def button_callback(interaction: discord.Interaction, option=option):
            await interaction.response.defer()
            # Save the next step to the trainer's data
            if "next" in option:
                trainer_data["position"]["story_step"] = option["next"]["step"]
                if "location" in option["next"]:
                    trainer_data["position"]["location"] = option["next"]["location"]
                elif "city" in option["next"]:
                    trainer_data["position"]["city"] = option["next"]["city"]

            # Handle the action dynamically
            if "action" in option:
                handler_name= option.get("handler")
                await handle_action(interaction, trainer_data, option["action"],handler_name=handler_name, pokemon_name=option.get("label"))
                update_trainer_location(trainer_data["user_id"],trainer_data["position"])

            # Render the next step
            await handle_button_click(interaction)

        button.callback = button_callback
        view.add_item(button)

    # Send the embed for the current step
    embed = make_embed(
        title=step_data["title"],
        description=step_data["description"]
    )
    if not interaction.response.is_done():
        await interaction.response.send_message(embed=embed, view=view)
    else:
        await interaction.followup.send(embed=embed, view=view)
    
@bot.slash_command(name="start", description="Begin your Pokemon adventure!")
async def start(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer_data = get_trainer_with_team(user_id=user_id)
    if trainer_data:
        await interaction.response.send_message(embed=make_embed(title="You are a trainer already"), ephemeral=True)
        return
    trainer_data = create_trainer(user_id, interaction.user.name)
    if trainer_data:
        await handle_button_click(interaction)

@bot.slash_command(name="continue", description="Continue your story from where you left off.")
async def continue_story(interaction: discord.Interaction):
    user_id = interaction.user.id
    trainer_data = get_trainer_with_team(user_id)
    if not trainer_data:
        await interaction.response.send_message(embed=make_embed(title="You are no trainer yet",description="Please use /start to start your journey"), ephemeral=True)
        return
    
    await handle_button_click(interaction)

# Finally, run the bot with the token from .env
bot.run(os.getenv('TOKEN'))
