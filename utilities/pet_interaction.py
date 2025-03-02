from functools import partial
import random
from unicodedata import category
import discord
from discord.ext import commands
from bot_util import get_attention_messages, load_items, make_embed
from utilities.commands import isPetStatsFine
from mongodb.owner import get_owner, update_inventory_usage, updateCommissionTarget
from mongodb.pet import update_pet
from pojos.BaseView import BackButton, BaseView, ConfirmView, DynamicDropdown
class ItemView(BaseView):
    def __init__(self, user_id,pet, food_items,category,amount=1):
        super().__init__(user_id=user_id)
        self.user_id = user_id
        self.food_items = food_items
        self.pet = pet
        self.amount=amount
        self.select_food = None
        self.og_message = None
        self.category = category
        # Create a dropdown with food items
        options = []
        for item in food_items:
            description = ""
            for effect in item.get("specialEffect",[]):
                description += f"{effect["name"]} (Chance: {effect["chance"]}%), \n"
            item["description"] = description.strip()
            options.append(item)
        self.food_dropdown = DynamicDropdown(
            user_id,
            options,
            amount,
            "Give your pet the following item",
            self.lable_format,
            self.select_item_callback
        )
        self.add_item(self.food_dropdown)
        
    def lable_format(self,item):
        if item["amount"] < self.amount:
            return f"{item["amount"]}x {item["name"]} - filling: {item["filling"]}"
        return f"{self.amount}x {item["name"]} - filling: {item["filling"]}"
    
    async def select_item_callback(self, interaction: discord.Interaction):
        self.select_food = next(item for item in self.food_items if item["name"] == self.food_dropdown.values[0])
        self.clear_items()  # Remove dropdown
        
        view = ConfirmView(self.user_id,self.confirm_callback)

        await interaction.response.send_message(
            content=f"Are you sure you want to give **{self.select_food['name']}**?",
            view=view
        )

    async def confirm_callback(self, interaction: discord.Interaction):
        
        amount = self.amount
        stat = "hunger"
        category = "eat"
        if self.select_food["typeOfItem"] == "drink":
            stat = "thirst"
            category = "drink"
        elif self.select_food["typeOfItem"] == "healing":
            stat = "health"
            category = "med"
            
        if self.select_food["amount"] < amount:
            amount = self.select_food["amount"]
        # Fill hunger
        self.pet[stat] = self.pet[stat] + (self.select_food["filling"]*amount)
        
        if amount >3:
            description = f"*{self.pet['nickname']}* looks at you shocked, nevertheless starts happily munchin on the {self.select_food['name']}. It restores {self.select_food['filling']*amount} {stat} points.\n"
        description = f"*{self.pet['nickname']}* happily munches on the {self.select_food['name']}. It restores {self.select_food['filling']*amount} {stat} points.\n"
        # Sickness Healing
        if self.pet["sick"] and category != "med":
            if self.pet["sick"].get("action"):
                if self.select_food["name"] == self.pet["sick"]["action"].get(category,{}).get("item"):
                    self.pet["sick"]["action"][category]["amount"]+=1*amount
                    if self.pet["sick"]["action"][category]["amount"] >= self.pet["sick"]["action"][category]["goal"]:
                        description += f"💊 Thanks to {self.select_food["name"]} your pet is healed from {self.pet["sick"]["name"]}\n"
                        self.pet["sick"]=None
        ## Med healing sickness
        if self.pet["sick"] and category == "med":
            if self.select_food["name"] == self.pet["sick"][category]:
                description += f"💊 Thanks to {self.select_food["name"]} your pet is healed from {self.pet["sick"]["name"]}\n"
                self.pet["sick"]=None
        
        # Apply special effects
        for i in range(amount):
            for effect in self.select_food.get("specialEffect", []):
                if random.randint(1, 100) <= effect["chance"]:
                    self.pet[effect["name"]] = self.pet.get(effect["name"], 0) + self.select_food["filling"]
                    description += f"✨ {effect['name']} increased by {self.select_food['filling']}!\n"

        # Check for favorite or hated food
        if self.select_food["name"] == self.pet["hates"]["food"]["name"]:
            self.pet["hates"]["food"]["discovered"] = True
            happiness_loss = int(self.select_food["filling"]*amount * 1.5)
            self.pet["happiness"] = max(0, round(self.pet["happiness"] - happiness_loss,1))
            description += f"*{self.pet['nickname']}* glares at you! **They absolutely hate this food!**\n💔 Lost {happiness_loss} happiness points.\n"

        elif self.select_food["name"] == self.pet["favorites"]["food"]["name"]:
            self.pet["favorites"]["food"]["discovered"] = True
            happiness_gain = int(self.select_food["filling"]*amount * 1.5)
            self.pet["happiness"] = self.pet["happiness"] + happiness_gain
            description += f"*{self.pet['nickname']}* wags its tail! **They LOVE this food!**\n💖 Gained {happiness_gain} happiness points!\n"

            # Small chance to boost commission target
            if random.randint(1, 500) == 1:
                commission_points = int(1.5 * self.pet["level"])
                description += f"🎯 Your bond strengthens! If you have set a **Commission target, it got increased by {commission_points} points.**\n"
                updateCommissionTarget(self.user_id, commission_points)

        # Update pet data and inventory
        result1 = update_inventory_usage(self.user_id, self.select_food,amount)
        await isPetStatsFine(self.pet)
        result2 = update_pet(self.user_id, self.pet)

        if result1 == 0 or result2 == 0:
            await interaction.response.edit_message(
                embed=make_embed(f"Somethign went wrong with this action. Prepare for data lost :D"),
                view=None  # Remove buttons
            )
            return
        user_data = get_owner(interaction.user.id)
        itemOptions = categoryItemOptionMaker(self.category,user_data["inventory"])

        if len(itemOptions)==0:
            self.clear_items()
            await self.og_message.edit(embed=make_embed(f"You don't have anything to {self.category} left!"))
        else:
            self.food_dropdown.changeOptions(itemOptions)
            self.clear_items()  # Removes old buttons/dropdowns
            self.add_item(self.food_dropdown)  # Re-add the updated dropdown
            await self.og_message.edit(embed=make_embed(f"Select the {self.category} to give:"),view=self)
        # Send confirmation message
        self.clear_items()
        await interaction.response.edit_message(
            embed=make_embed(f"You give *{self.pet['nickname']}*  **{self.select_food['name']}**!", description=description),
            view=None  # Remove buttons
        )

async def itemGiveView(ctx: discord.ApplicationContext,category, user_data,amount):
    itemOptions = categoryItemOptionMaker(category,user_data["inventory"])
    if not itemOptions:
        await ctx.response.send_message(embed=make_embed(f"You don't have anything to {category}!"), ephemeral=True)
        return
    view = ItemView(user_data["user_id"],user_data["pet"][0], itemOptions,category,amount)
    await ctx.response.defer()
    message = await ctx.followup.send(content=f"Select the {category} to give:", view=view)
    view.og_message = message

def categoryItemOptionMaker(category, items):
    itemOptions=[]
    if category == "eat":
        itemOptions = [item for item in items if item.get("typeOfItem") == "food"]
    elif category == "drink":
        itemOptions = [item for item in items if item.get("typeOfItem") == "drink"]
    else:
        itemOptions = [item for item in items if item.get("typeOfItem") != "drink" and item.get("typeOfItem") != "food"] 
    return itemOptions
## ------ Attention ------
class AttentionView(BaseView):
    def __init__(self, user_data):
        super().__init__(user_id= user_data["user_id"])
        self.user_data = user_data  # Store user data for processing
        self.latest_message = None
        
        self.add_item(BackButton(user_data["user_id"],label="Pat",emoji="🤚", callback=partial(self.attention_action,action_name="pat")))
        self.add_item(BackButton(user_data["user_id"],label="Cuddles",emoji="🫂", callback=partial(self.attention_action,action_name="cuddles")))

        
    async def attention_action(self, interaction: discord.Interaction, action_name: str):
        """Handles different attention actions"""
        pet = get_owner(self.user_data["user_id"])["pet"][0]
        #pet = self.user_data["pet"][0]
        
        ## Overloaded silly time
        if pet.get("sick"):
            if pet["sick"]["name"] == "Overstimulated":
                await interaction.response.edit_message(
                    embed=make_embed(f"{pet['nickname']} feels too happy!"),
                    view=None
                )
                await interaction.message.add_reaction("💥")
                return
        
        message_actions = get_attention_messages(action_name,pet["species"], pet["nickname"],pet["mood"]["name"])
        message_type_action = []
        # Apply action effect (Modify pet's mood or stats if needed)
        if random.randint(0,100)>90:
            if random.randint(0,1)==1:
                message_type_action = [message for message in message_actions if message["type"]=="negative"]
            else:
                message_type_action = [message for message in message_actions if message["type"]!="negative" or message["type"]=="positive"]
        else:
            message_type_action = [message for message in message_actions if message["type"]=="positive"]
        message = random.choice(message_type_action)
        pet["health"] +=  message.get("health",0)
        pet["energy"] +=  message.get("energy",0)
        pet["happiness"] +=  message.get("happiness",0)
        
        await isPetStatsFine(pet)    
        update_pet(self.user_data["user_id"], pet)
        #add mon
        addon = ""
        if message.get("health"):
            addon = f"Health: {message.get("health",0)}"
        elif message.get("energy"):
            addon = f"Energy: {message.get("energy",0)}"
        
        message = f"{message["message"]}\n-# Happiness: {message.get("happiness",0)}; {addon}"
        if self.latest_message:
           await self.latest_message.delete()
           self.latest_message = None

        if not self.latest_message:
            await interaction.response.defer()
            response  = await interaction.followup.send(embed=make_embed(f"You try to give {pet['nickname']} {action_name} ",  message))
            self.latest_message = await interaction.channel.fetch_message(response.id)  
        
'''
    @discord.ui.button(label="Talk", emoji="🗣️", style=discord.ButtonStyle.primary)
    async def talk_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_action(interaction, "talk")

    @discord.ui.button(label="Treat", emoji="🍪", style=discord.ButtonStyle.success)
    async def treat_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_action(interaction, "treat")

    @discord.ui.button(label="Rubs", emoji="💆", style=discord.ButtonStyle.success)
    async def rubs_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_action(interaction, "rubs")'''
        
    