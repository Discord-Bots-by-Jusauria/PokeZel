import random
import discord
from discord.ext import commands
from bot_util import make_embed
from mongodb.owner import get_owner, update_inventory_usage, updateCommissionTarget
from mongodb.pet import update_pet

class FeedView(discord.ui.View):
    def __init__(self, user_id,pet, food_items):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.food_items = food_items
        self.pet = pet

        # Create a dropdown with food items
      
        for item in food_items:
            description = ""
            for effect in item.get("specialEffect",[]):
                description += f"{effect["name"]} (Chance: {effect["chance"]}%), \n"
            options = [
                discord.SelectOption(label=f"{item["name"]} - filling: {item["filling"]}", description=description, value=item["name"])
            ]
        self.food_dropdown = discord.ui.Select(placeholder="Select food to feed", options=options)
        self.food_dropdown.callback = self.select_food
        self.add_item(self.food_dropdown)

    async def select_food(self, interaction: discord.Interaction):
        selected_food = next(item for item in self.food_items if item["name"] == self.food_dropdown.values[0])
        self.clear_items()  # Remove dropdown
        self.add_item(ConfirmButton(self.user_id, selected_food, self.pet))  # Add confirm button

        await interaction.response.edit_message(
            content=f"Are you sure you want to feed **{selected_food['name']}**?",
            view=self
        )

class ConfirmButton(discord.ui.Button):
    def __init__(self, user_id, selected_food, pet):
        super().__init__(label="Confirm", style=discord.ButtonStyle.green)
        self.user_id = user_id
        self.food = selected_food
        self.pet = pet

    async def callback(self, interaction: discord.Interaction):
        # Fill hunger
        self.pet["hunger"] = min(100, self.pet["hunger"] + self.food["filling"])
        description = f"*{self.pet['nickname']}* happily munches on the {self.food['name']}. It restores {self.food['filling']} hunger points.\n"

        # Apply special effects
        for effect in self.food.get("specialEffects", []):
            if random.randint(1, 100) <= effect["chance"]:
                self.pet[effect["name"]] = min(100, self.pet.get(effect["name"], 0) + self.food["filling"])
                description += f"✨ {effect['name']} increased by {self.food['filling']}!\n"

        # Check for favorite or hated food
        if self.food["name"] == self.pet["hates"]["food"]["name"]:
            self.pet["hates"]["food"]["discovered"] = True
            happiness_loss = int(self.food["filling"] * 1.5)
            self.pet["happiness"] = max(0, self.pet["happiness"] - happiness_loss)
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

    await ctx.response.send_message(content="Select the food to feed:", view=FeedView(user_data["user_id"],user_data["pet"][0], food_items))
