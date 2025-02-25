import random
from unicodedata import category
import discord
from discord.ext import commands
from bot_util import get_attention_messages, make_embed
from mongodb.owner import get_owner, update_inventory_usage, updateCommissionTarget
from mongodb.pet import update_pet

class ItemView(discord.ui.View):
    def __init__(self, user_id,pet, food_items):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.food_items = food_items
        self.pet = pet
        async def on_timeout(self):
            """Disable all buttons when the timeout is reached."""
            for child in self.children:
                if isinstance(child, discord.ui.Button):
                    child.disabled = True  # Disable buttons
        # Create a dropdown with food items
        options = []
        for item in food_items:
            description = ""
            for effect in item.get("specialEffect",[]):
                description += f"{effect["name"]} (Chance: {effect["chance"]}%), \n"
            
            options.append(discord.SelectOption(label=f"{item["name"]} - filling: {item["filling"]}", description=description, value=item["name"]))
        self.food_dropdown = discord.ui.Select(placeholder="Select the item to give", options=options)
        self.food_dropdown.callback = self.select_food
        self.add_item(self.food_dropdown)

    async def select_food(self, interaction: discord.Interaction):
        selected_food = next(item for item in self.food_items if item["name"] == self.food_dropdown.values[0])
        self.clear_items()  # Remove dropdown
        self.add_item(ConfirmButton(self.user_id, selected_food, self.pet))  # Add confirm button

        await interaction.response.edit_message(
            content=f"Are you sure you want to give **{selected_food['name']}**?",
            view=self
        )

class ConfirmButton(discord.ui.Button):
    def __init__(self, user_id, selected_food, pet):
        super().__init__(label="Confirm", style=discord.ButtonStyle.green)
        self.user_id = user_id
        self.food = selected_food
        self.pet = pet

    async def callback(self, interaction: discord.Interaction):
        stat = "hunger"
        category = "eat"
        if self.food["typeOfItem"] == "drink":
            stat = "thirst"
            category = "drink"
        elif self.food["typeOfItem"] == "healing":
            stat = "health"
            category = "med"
        # Fill hunger
        self.pet[stat] = min(100, self.pet[stat] + self.food["filling"])
        description = f"*{self.pet['nickname']}* happily munches on the {self.food['name']}. It restores {self.food['filling']} {stat} points.\n"
        # Sickness Healing
        if self.pet["sick"] and category != "med":
            if self.pet["sick"]["action"]:
                if self.food["name"] == self.pet["sick"]["action"].get(category,{}).get("item"):
                    self.pet["sick"]["action"][category]["amount"]+=1
                    if self.pet["sick"]["action"][category]["amount"] == self.pet["sick"]["action"][category]["goal"]:
                        description += f"💊 Thanks to {self.food["name"]} your pet is healed from {self.pet["sick"]["name"]}\n"
                        self.pet["sick"]=None
        ## Med healing sickness
        if self.pet["sick"] and category == "med":
            if self.food["name"] == self.pet["sick"][category]:
                description += f"💊 Thanks to {self.food["name"]} your pet is healed from {self.pet["sick"]["name"]}\n"
                self.pet["sick"]=None
        
        # Apply special effects
        for effect in self.food.get("specialEffects", []):
            if random.randint(1, 100) <= effect["chance"]:
                self.pet[effect["name"]] = min(100, self.pet.get(effect["name"], 0) + self.food["filling"])
                description += f"✨ {effect['name']} increased by {self.food['filling']}!\n"

        # Check for favorite or hated food
        if self.food["name"] == self.pet["hates"]["food"]["name"]:
            self.pet["hates"]["food"]["discovered"] = True
            happiness_loss = int(self.food["filling"] * 1.5)
            self.pet["happiness"] = max(0, round(self.pet["happiness"] - happiness_loss,1))
            description += f"*{self.pet['nickname']}* glares at you! **They absolutely hate this food!**\n💔 Lost {happiness_loss} happiness points.\n"

        elif self.food["name"] == self.pet["favorites"]["food"]["name"]:
            self.pet["favorites"]["food"]["discovered"] = True
            happiness_gain = int(self.food["filling"] * 1.5)
            self.pet["happiness"] = min(100, self.pet["happiness"] + happiness_gain)
            description += f"*{self.pet['nickname']}* wags its tail! **They LOVE this food!**\n💖 Gained {happiness_gain} happiness points!\n"

            # Small chance to boost commission target
            if random.randint(1, 500) == 1:
                commission_points = int(1.5 * self.pet["level"])
                description += f"🎯 Your bond strengthens! If you have set a **Commission target, it got increased by {commission_points} points.**\n"
                updateCommissionTarget(self.user_id, commission_points)

        # Update pet data and inventory
        result1 = update_inventory_usage(self.user_id, self.food,1)
        result2 = update_pet(self.user_id, self.pet)

        if result1 == 0 or result2 == 0:
             await interaction.response.edit_message(
            embed=make_embed(f"Somethign went wrong with feeding."),
            view=None  # Remove buttons
        )
        
        # Send confirmation message
        await interaction.response.edit_message(
            embed=make_embed(f"You give *{self.pet['nickname']}* a **{self.food['name']}**!", description=description),
            view=None  # Remove buttons
        )

async def feedView( ctx: discord.ApplicationContext, user_data):
    food_items = [item for item in user_data["inventory"] if item.get("typeOfItem") == "food"]
    
    if not food_items:
        await ctx.response.send_message(embed=make_embed("You don't have any food to feed your pet!"), ephemeral=True)
        return

    await ctx.response.send_message(content="Select the food to feed:", view=ItemView(user_data["user_id"],user_data["pet"][0], food_items))
async def drinkView( ctx: discord.ApplicationContext, user_data):
    food_items = [item for item in user_data["inventory"] if item.get("typeOfItem") == "drink"]
    
    if not food_items:
        await ctx.response.send_message(embed=make_embed("You don't have any drinks to give your pet!"), ephemeral=True)
        return

    await ctx.response.send_message(content="Select the drink to give:", view=ItemView(user_data["user_id"],user_data["pet"][0], food_items))
async def itemView( ctx: discord.ApplicationContext, user_data):
    food_items = [item for item in user_data["inventory"] if item.get("typeOfItem") != "drink" or item.get("typeOfItem") != "food"] 
    
    if not food_items:
        await ctx.response.send_message(embed=make_embed("You don't have any drinks to give your pet!"), ephemeral=True)
        return

    await ctx.response.send_message(content="Select the drink to give:", view=ItemView(user_data["user_id"],user_data["pet"][0], food_items))


## ------ Attention ------
import discord


class AttentionView(discord.ui.View):
    def __init__(self, user_data, timeout=120):
        super().__init__(timeout=timeout)
        self.user_data = user_data  # Store user data for processing

    async def handle_action(self, interaction: discord.Interaction, action_name: str):
        """Handles different attention actions"""
        pet = self.user_data["pet"][0]
        
        message_action = get_attention_messages(action_name,pet["species"], pet["nickname"],pet["mood"]["name"])
        # Apply action effect (Modify pet's mood or stats if needed)
        pet["mood"]["value"] = min(100, pet["mood"]["value"] + mood_boost)

        await interaction.response.send_message(embed=make_embed(response_text, f"{pet['nickname']} looks happy!"), ephemeral=True)

    @discord.ui.button(label="Pat", emoji="🤚", style=discord.ButtonStyle.primary)
    async def pat_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_action(interaction, "Pat")

    @discord.ui.button(label="Cuddles", emoji="🤗", style=discord.ButtonStyle.primary)
    async def cuddles_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_action(interaction, "Cuddles")

    @discord.ui.button(label="Talk", emoji="🗣️", style=discord.ButtonStyle.primary)
    async def talk_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_action(interaction, "Talk")

    @discord.ui.button(label="Treat", emoji="🍪", style=discord.ButtonStyle.success)
    async def treat_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_action(interaction, "Treat")

    @discord.ui.button(label="Rubs", emoji="💆", style=discord.ButtonStyle.success)
    async def rubs_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_action(interaction, "Rubs")