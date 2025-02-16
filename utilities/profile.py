
from collections import defaultdict
from datetime import datetime
import discord
from bot_util import make_embed
from utilities.time import checkBdayToday, secondsUntil14h

class ProfileView(discord.ui.View):
    def __init__(self, user_data):
        super().__init__(timeout=None)  # Persistent view
        self.user_data = user_data

    @discord.ui.button(label="Inventory", style=discord.ButtonStyle.primary, custom_id="profile_view:inventory")
    async def inventory_button(self, button: discord.Button, interaction: discord.Interaction):
        await show_inventory(interaction, self.user_data)


class InventoryView(discord.ui.View):
    def __init__(self, user_data):
        super().__init__(timeout=None)  # Persistent view
        self.user_data = user_data

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary, custom_id="inventory_view:back")
    async def back_button(self, button: discord.Button, interaction: discord.Interaction):
        await show_profile(interaction, self.user_data)


async def show_profile(interaction: discord.Interaction, user_data):
    embed = make_embed(user_data["user_name"])
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    ## Profile user Details
    embed.add_field(name="Points", value=user_data["points"])
    embed.add_field(name="Rank", value=user_data["rank"])
    if user_data.get("bday"):
        bday = datetime.fromtimestamp(user_data["bday"])
        value = f"{bday.month:02d}-{bday.day:02d}"
        if checkBdayToday(user_data["bday"]):
            value += "  == 🎉🎂"
        embed.add_field(name="B-day (MM-DD)",value= value, inline=False)
    
    ## Daily To-Dos
    check_in_time = secondsUntil14h(user_data["check-in"])
    check_in_display = "✅" if check_in_time == 0 else f"` {check_in_time}s `"
    value = f"Check-in: {check_in_display}\n"
    value +=f"Daily Pet Task:  {user_data["commission_target"]["name"] + 
                        " (" + str(user_data["commission_target"]["amount"]) + 
                        "/" + str(user_data["commission_target"]["goal"]) + ")"}"
    embed.add_field(name="Today's To-Dos: ", value=value,inline=False)
   ## embed.add_field(name="Daily Pet Task:", 
               ##     value=user_data["commission_target"]["name"] + 
          ##              " (" + str(user_data["commission_target"]["amount"]) + 
##"/" + str(user_data["commission_target"]["goal"]) + ")")
    ## Set Values and Goals
    embed.add_field(name="Commission target:", 
                    value=user_data["commission_target"]["name"] + 
                        " (" + str(user_data["commission_target"]["amount"]) + 
                        "/" + str(user_data["commission_target"]["goal"]) + ")",inline=False)
    embed.add_field(name="Started", value=f"<t:{str(user_data.get('start_of_game', 0))}:F>", inline=False)
    # Create and attach ProfileView
    view = ProfileView(user_data=user_data)

    # Send or Edit Message
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, view=view)
    else:
        await interaction.response.send_message(embed=embed, view=view)


async def show_inventory(interaction: discord.Interaction, user_data):

    # Assume 'inventory' is a dictionary with categories as keys and list of items as values
    inventory = user_data.get('inventory', {})

    # Create Inventory Embed
    embed = make_embed(title="Inventory", description="")

    if not inventory:
        embed.add_field(name="Inventory", value="No items in inventory.", inline=False)
    else:
        # Step 1: Group items by category
        category_dict = defaultdict(list)
        for item in inventory:
            category = item.get('typeOfItem', 'Uncategorized')  # Default to 'Uncategorized' if category is missing
            category_dict[category].append(item)

        # Step 2: Iterate through each category and sort items by name
        for category, items in sorted(category_dict.items()):
            if not items:
                # If there are no items in this category, indicate so
                embed.add_field(name=category.capitalize(), value="No items.", inline=False)
                continue
            
            # Sort items alphabetically by 'name'
            sorted_items = sorted(items, key=lambda x: x.get('name', '').lower())
            
            # Step 3: Create a string listing all items in this category
            # Format: Item Name xQuantity - Cost
            # Assuming you have a 'quantity' field; if not, you can omit it or set a default value
            item_lines = []
            for item in sorted_items:
                name = item.get('name', 'Unknown')
                quantity = item.get('amount', 1)
                short_text = f"Filling: {item["filling"]}; Effects: "
                for effect in item["specialEffect"]:
                    short_text+= f"{effect["name"]} (Chance: {effect["chance"]}%), "
                # You can customize the format as needed
                line = f"**{name}** x{quantity} - {short_text} "
                item_lines.append(line)
            
            # Join all item lines into a single string separated by newlines
            item_list = "\n\n".join(item_lines)
            
            # Add the category and its items as a field in the embed
            embed.add_field(name=category.capitalize(), value=item_list, inline=True)

    # Create and attach InventoryView
    view = InventoryView(user_data=user_data)

    # Edit the original message with the Inventory embed and view
    await interaction.response.edit_message(embed=embed, view=view)

async def show_pet_profile(interaction: discord.Interaction, user_data):
    pet = user_data["pet"]
    if user_data["pet_slot_available"]==1:
        pet = pet[0]
        embed = make_embed(pet["species"])
        file = discord.File("assets/alpha.png", filename="alpha.png")
        embed.set_thumbnail(url="attachment://alpha.png")
        ## Basic data
        embed.add_field(name="Nickname", value=pet["nickname"])
        value = f"{pet["level"]} \n({pet["exp"]["current"]}/{pet["exp"]["goal"]})"
        embed.add_field(name="Level", value=value)
        embed.add_field(name="Type", value=pet["type"])
        embed.add_field(name="Holding Special", value=pet["item_hold"]["special"],inline=False)
        ## Statues of living
        value = f"Hunger: {pet["hunger"]}\n"
        value+= f"thirst: {pet["thirst"]}\n"
        value+= f"Health: {pet["health"]}\n"
        value+= f"Happiness: {pet["happiness"]}\n"
        value+= f"Intelligence: {pet["intelligence"]}\n"
        embed.add_field(name="Status:",value=value,inline=False)
        ## Fav things
        value = f"Drink: {pet['favorites']['drink']['name'] if pet['favorites']['drink']['discovered'] else '???'}\n" \
        f"Food: {pet['favorites']['food']['name'] if pet['favorites']['food']['discovered'] else '???'}\n" 
        value2= f"Drink: {pet['hates']['drink']['name'] if pet['hates']['drink']['discovered'] else '???'}\n" \
        f"Food: {pet['hates']['food']['name'] if pet['hates']['food']['discovered'] else '???'}"
        embed.add_field(name="Likes", value=value)
        embed.add_field(name="Hates", value=value2)
        ## Holding Slots
        value=f"Slot 1: {pet["item_hold"]["slot1"]}\n"\
        f"Slot 2: {pet["item_hold"]["slot2"]}\n"\
        f"Slot 3: {pet["item_hold"]["slot3"]}\n"  
        embed.add_field(name="Item Slots", value=value,inline=False)  
    
    await interaction.response.send_message(embed=embed, file=file)