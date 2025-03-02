
from collections import defaultdict
from datetime import datetime
from pickle import TRUE
import discord
from bot_util import make_embed
from utilities.time import checkBdayToday, secondsUntil12h
from pojos.BaseView import BackButton, BaseView, DynamicDropdown

class ProfileView(BaseView):
    def __init__(self, user_data):
        super().__init__(user_id=user_data["user_id"])
        self.user_data = user_data

        # Add Inventory Button
        self.add_item(BackButton(user_data["user_id"], label="Inventory", callback=self.show_inventory))

    async def show_inventory(self, interaction: discord.Interaction):
        """Opens the inventory view."""
        await show_inventory(interaction, self.user_data)
class InventoryView(BaseView):
    def __init__(self, user_data):
        super().__init__(user_id=user_data["user_id"])
        self.user_data = user_data

        # Add Back Button
        self.add_item(BackButton(user_data["user_id"], label="Back", callback=self.show_profile))

    async def show_profile(self, interaction: discord.Interaction):
        """Returns to profile view."""
        await show_profile(interaction, self.user_data, True)
class PetView(BaseView):
    def __init__(self, user_data):
        super().__init__(user_id=user_data["user_id"])
        self.user_data = user_data
        
        itemOptions = [{"name":"eat","label":"Feed the Pet"},{"name":"drink","label":"Drench the Pet"},{"name":"offer","label":"Give the Pet an item"},{"name":"attention","label":"Give the pet attention and love"},{"name":"sleep","label":"Sleeping Burrito >:3"}]
        self.dropdown = DynamicDropdown(user_data["user_id"],itemOptions,1,"Choose a quick action selection",self.formatDropdown,self.selectedAction)
        self.add_item(self.dropdown)
        
        # Add Inventory Button
        self.add_item(BackButton(user_data["user_id"], label="Personality", callback=self.personality))
        
        
    def formatDropdown(self,item):
        return f"{item["label"]}"
    async def selectedAction(self, interaction: discord.Interaction):
        action = self.dropdown.values[0]
        pet_cog = interaction.client.get_cog("Pet")
        
        if not pet_cog:
            await interaction.response.send_message("Upsy. This command doesn't exist yet ^^", ephemeral=True)
            return
        ctx = await interaction.client.get_application_context(interaction)
        
        if action == "eat":
            await pet_cog.feed.callback(pet_cog,ctx)
        elif action == "drink":
            await pet_cog.drench.callback(pet_cog,ctx)
        elif action == "offer":
            await pet_cog.offer.callback(pet_cog,ctx)
        elif action == "sleep":
            await pet_cog.sleep.callback(pet_cog,ctx)
        elif action == "attention":
            await pet_cog.attention.callback(pet_cog,ctx)
        
    async def personality(self, interaction: discord.Interaction):
        """Opens the inventory view."""
        await show_pet_personality(interaction, self.user_data)
class PersonalityView(BaseView):
    def __init__(self, user_data):
        super().__init__(user_id=user_data["user_id"])
        self.user_data = user_data

        # Add Inventory Button
        self.add_item(BackButton(user_data["user_id"], label="Back", callback=self.profile))

    async def profile(self, interaction: discord.Interaction):
        """Opens the inventory view."""
        await show_pet_profile(interaction, self.user_data,True)
        
async def show_profile(interaction: discord.Interaction, user_data, back=False):
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
    embed.add_field(name="Commission target:", 
                    value=user_data["commission_target"]["name"] + 
                        " (" + str(user_data["commission_target"]["amount"]) + 
                        "/" + str(user_data["commission_target"]["goal"]) + ")",inline=False)
    ## Daily To-Dos
    check_in_time = secondsUntil12h(user_data["check-in"])
    check_in_display = "✅" if check_in_time == 0 else f"` {check_in_time}s `"
    value = f"Check-in: {check_in_display}\n"
    value +=f"Daily Pet Task:  {user_data["commission_target"]["name"] + 
                        " (" + str(user_data["commission_target"]["amount"]) + 
                        "/" + str(user_data["commission_target"]["goal"]) + ")"}"
    embed.add_field(name="Today's To-Dos: ", value=value,inline=False)
    
    embed.add_field(name="Difficulty", value=f"{user_data["difficulty"]}", inline=True)
    embed.add_field(name="Notifications", value=f"{user_data.get("notifications","normal")}", inline=True)
    embed.add_field(name="Started", value=f"<t:{str(user_data.get('start_of_game', 0))}:F>", inline=False)
    # Create and attach ProfileView
    view = ProfileView(user_data=user_data)

    # Send or Edit Message
    if back:
        await interaction.response.edit_message(embed=embed, view=view)
        return
    await interaction.response.send_message(embed=embed,view=view)
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
            item_list = "\n\n"
            for i in range(len(item_lines)):
                item_list += f"{item_lines[i]}\n"
                print(item_list)
                if i%5 ==0:
                    embed.add_field(name=category.capitalize(), value=item_list, inline=True)
                    item_list = "\n\n"

    # Create and attach InventoryView
    view = InventoryView(user_data=user_data)

    # Edit the original message with the Inventory embed and view
    await interaction.response.edit_message(embed=embed, view=view)


async def show_pet_profile(interaction: discord.Interaction, user_data, back=False):
    pet = user_data["pet"][0]
    if user_data["pet_slot_available"] == 1:
        # Page 1: General Information
        addon = ""
        if pet.get("is_sleeping", False):
            addon = " 💤"
        if pet.get("died",False):
             addon = " ☠️"
        embed1 = make_embed(f"{pet["species"]} {addon}")
        file1 = discord.File("assets/alpha.png", filename="alpha.png")
        embed1.set_thumbnail(url="attachment://alpha.png")
        
        # Basic Data
        embed1.add_field(name="Nickname", value=pet["nickname"], inline=False)
        value = f"{pet['level']} \n({pet['exp']['current']}/{pet['exp']['goal']})"
        embed1.add_field(name="Level", value=value)
        embed1.add_field(name="Type", value=pet["type"])
        embed1.add_field(name="Holding Special", value=pet["item_hold"]["special"])
        # Mood
        mood = pet["mood"]["name"] # Example mood based on happiness
        embed1.add_field(name="Mood", value=mood)
        # Sick
        if pet.get("sick"):
            embed1.add_field(name="Sickness", value=pet["sick"]["name"])
        # Statues of Living
        value=""
        value += f":sparkling_heart: Health: {pet['health']}%\n"
        value += f":fork_and_knife: Hunger: {pet['hunger']}%\n"
        value += f":ocean: Thirst: {pet['thirst']}%\n"
        value += f":zap: Energy: {pet['energy']}%\n"
        value += f":sparkles: Happiness: {pet['happiness']}%\n"
        value += f":books: Intelligence: {pet['intelligence']}%\n"
        
        embed1.add_field(name="Status", value=value, inline=False)
        file2 = discord.File("assets/alpha.png", filename="alpha.png")
        view = PetView(user_data)
        # Send or Edit Message
        if back:
            await interaction.response.edit_message(embed=embed1, view=view,file=file2)
            return
        await interaction.response.send_message(embed=embed1,view=view, file=file2)
async def show_pet_personality(interaction: discord.Interaction, user_data):
    pet = user_data["pet"][0]
    # Page 1: General Information
    addon = ""
    if pet.get("is_sleeping", False):
        addon = " 💤"
    if pet.get("died",False):
            addon = " ☠️"

    # Page 2: Additional Information
    embed2 = make_embed(f"{pet["species"]}{addon}")
    embed2.set_thumbnail(url="attachment://alpha.png")
    # Personality and Evolution Options
    embed2.add_field(name="Personality", value=pet["personality"]["name"], inline=False)
    # Favorite and Hated Things
    value = f"Drink: {pet['favorites']['drink']['name'] if pet['favorites']['drink']['discovered'] else '???'}\n" \
            f"Food: {pet['favorites']['food']['name'] if pet['favorites']['food']['discovered'] else '???'}"
    value2 = f"Drink: {pet['hates']['drink']['name'] if pet['hates']['drink']['discovered'] else '???'}\n" \
                f"Food: {pet['hates']['food']['name'] if pet['hates']['food']['discovered'] else '???'}"
    embed2.add_field(name="Likes", value=value)
    embed2.add_field(name="Hates", value=value2)

    # Holding Slots
    value = f"Slot 1: {pet['item_hold']['slot1']}\n" \
            f"Slot 2: {pet['item_hold']['slot2']}\n" \
            f"Slot 3: {pet['item_hold']['slot3']}\n"
    embed2.add_field(name="Item Slots", value=value, inline=False)
    
    value=f"Current Stage: {pet['stage']}\n"
    value+=f"{pet['evolution'][0]} - {pet['evolution'][1]} - {pet['evolution'][2]}\n"
    embed2.add_field(name="Evolution Info", value=value, inline=False)

    # Create View for Buttons
    file2 = discord.File("assets/alpha.png", filename="alpha.png")
    view = PersonalityView(user_data)

    # Send the first page to the user
    await interaction.response.edit_message(embed=embed2, view=view, file=file2)