import discord
from discord.ext import commands

# Falls du fetch_profile_data nutzt, importiere es hier.
from bot_util import make_embed
from mongodb.pokemon import registeres_pokedex_pokemon_name
from mongodb.trainer import get_trainer_with_team
from pojos.emoji_handle import app_emojis, get_emoji, get_item_emoji
from services.MarketHandler import MarketHandler
from services.handlerList import ALL_HANDLERS
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

    @discord.command(name="buy", description="Purchase an item from the marketplace.")
    async def buy(self, interaction: discord.ApplicationContext):
        user_id = interaction.user.id
        user_data = get_trainer_with_team(user_id)
        handler =  ALL_HANDLERS.get(user_data["position"]["city"])
        area_date = await handler.load_story_data()
        if not user_data:
            await interaction.followup.send(embed=make_embed("No Trainer Found"))
            return
        
        location = user_data["position"]["location"] 
        story_step = user_data["position"]["story_step"]  
        step = next(step[story_step] for step in area_date["locations"][location] if story_step in step)

        if step["type"] != 'market':
            await interaction.response.send_message(embed=make_embed("You are not in front of a market stand."), ephemeral=True)
            return
            
        available_items = await ALL_HANDLERS.get("market").getMarketOffers(listType=step["title"], placeHandler=handler)
        if not available_items:
            await interaction.response.send_message(embed=make_embed("No items available for purchase at this time."), ephemeral=True)
            return
        
        # Create the select options
        options = [
            discord.SelectOption(
                label=f"{item['label']} - ${item['cost']}",
                value=item["value"]
            ) for item in available_items
        ]
        
        # Create the select menu
        select = discord.ui.Select(
            placeholder="Choose an item to buy...",
            min_values=1,
            max_values=1,
            options=options
        )
        
        # Define the callback for selection
        async def select_callback(interaction: discord.Interaction):
            selected_value = select.values[0]
            selected_item = next((item for item in available_items if item['value'] == selected_value), None)
            
            if not selected_item:
                await interaction.response.send_message("Item not found. :(", ephemeral=True)
                return
            
            if user_data['dollar'] < selected_item['cost']:
                await interaction.response.send_message(embed=make_embed("Are you kidding me? You don't have enough money."), ephemeral=True)
                return
            itemSaved ={
                "name":selected_item["value"],
                "cost" :selected_item["cost"],
                "attributes": selected_item["attributes"],
                "category" :selected_item["category"],
                "shortText":selected_item["shortText"]
            }
            success =  await ALL_HANDLERS.get("trainer").buy(user_data["user_id"],itemSaved)
            
            if success:
                await interaction.response.send_message(embed=make_embed(f"You bought **{selected_item['label']}**  ","It is now in your inventory to see and use."), ephemeral=True)
            else:
                await interaction.response.send_message(embed=make_embed("It seems the Seller doesn't trust you. Try again someday else."), ephemeral=True)
        
        # Attach the callback to the select menu
        select.callback = select_callback
        
        # Create a view and add the select menu
        view = discord.ui.View()
        view.add_item(select)
        
        # Send the message with the dropdown
        await interaction.response.send_message(embed=make_embed("Select an item to purchase:"), view=view, ephemeral=True)

def setup(bot):
    bot.add_cog(Player(bot))
