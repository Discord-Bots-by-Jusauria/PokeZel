import discord
from discord.ui import View, Select, Button
from discord import Embed, Interaction
from bot_util import load_items, make_embed
from mongodb.owner import buyItem, get_owner, sellItem



def categorize_items(items):
    categories = {}
    for item in items:
        category = item["typeOfItem"]
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    return categories

def create_shop_embed(category, items, money):
    embed = make_embed(f"Shop - Points: {money}", description=f"Category: {category.capitalize()}")

    for i, item in enumerate(items):
        if category == "evolution" and i % 2 == 0:
            embed.add_field(name="", value="", inline=False)  # Adds spacing every 2 items

        embed.add_field(
            name=f"{item['name']} ",
            value=f"Price: {item['price']}p\nFilling: {item['filling']}",
        )
    
    return embed

class ShopView(View):
    def __init__(self, user_id, money, categories, current_category, amount):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.money = money
        self.categories = categories
        self.category_list = list(categories.keys())  # Ordered category list
        self.current_category_index = self.category_list.index(current_category)
        self.amount = amount
        self.dropdown = Select(
            placeholder="Select an item to buy...",
            options=self.get_item_options(),
            custom_id="item_select"
        )
        self.dropdown.callback = self.select_item
        self.add_item(self.dropdown)

        self.update_buttons()
    async def on_timeout(self):
        
        """Disable all buttons when the timeout is reached."""
        for child in self.children:
            if isinstance(child, discord.ui.Button) or isinstance(child, Select):
                child.disabled = True  # Disable buttons
    def get_item_options(self):
        """Create dropdown options for the current category."""
        current_category = self.category_list[self.current_category_index]
        items = self.categories[current_category]

        return [
            discord.SelectOption(label=f"{item["name"]} - {item['price']*self.amount}p", value=item["name"])
            for item in items
        ]

    async def select_item(self, interaction: Interaction):
        """Handle item selection, which acts as a buy button."""
        selected_item_name = self.dropdown.values[0]
        selected_item = next(
            (item for item in self.categories[self.category_list[self.current_category_index]] if item["name"] == selected_item_name),
            None
        )

        if selected_item:
            # Show confirmation view immediately
            await interaction.response.send_message(
                embed=Embed(title=f"Buy {self.amount}x {selected_item['name']} for {selected_item['price']*self.amount}p?"),
                view=ConfirmPurchaseView(self.user_id, selected_item, self.money, confirm_purchase,self.amount),
                ephemeral=True
            )

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your shop!", ephemeral=True)
            return False
        return True

    def update_buttons(self):
        """Update navigation buttons' state."""
        self.previous_page.disabled = self.current_category_index == 0
        self.next_page.disabled = self.current_category_index == len(self.category_list) - 1

    @discord.ui.button(label="◀", style=discord.ButtonStyle.primary)
    async def previous_page(self, button: Button, interaction: Interaction):
        if self.current_category_index > 0:
            self.current_category_index -= 1
            self.dropdown.options = self.get_item_options()
            await self.update_shop(interaction)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.primary)
    async def next_page(self, button: Button, interaction: Interaction):
        if self.current_category_index < len(self.category_list) - 1:
            self.current_category_index += 1
            self.dropdown.options = self.get_item_options()
            await self.update_shop(interaction)

    async def update_shop(self, interaction: Interaction):
        """Update the shop page when navigating categories."""
        current_category = self.category_list[self.current_category_index]
        items = self.categories[current_category]

        self.update_buttons()
        embed = create_shop_embed(current_category, items, self.money)

        await interaction.response.edit_message(embed=embed, view=self)


async def buyView(interaction: discord.ApplicationContext, user_data, amount):
    items = load_items("items.json")
    money = user_data['points']
    #Stage filtering for items
    pet_stage = user_data["pet"][0]["stage"]  # Assuming the pet's stage is stored like this
    filtered_items = [item for item in items if item.get("stage",1) <= pet_stage]
    items = filtered_items
    categories = categorize_items(items)
    
    
    first_category = list(categories.keys())[0]
    shop_view = ShopView(user_id=user_data["user_id"], money=money, categories=categories, current_category=first_category, amount=amount)
    
    embed = create_shop_embed(first_category, categories[first_category], money)
    await interaction.response.send_message(embed=embed, view=shop_view)

class ConfirmPurchaseView(View):
    def __init__(self, user_id, item, money, callback, amount):
        super().__init__()
        self.user_id = user_id
        self.item = item
        self.money = money
        self.callback = callback
        self.amount = amount

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your purchase!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
    async def confirm(self, button: Button, interaction: Interaction):
        owner = get_owner(self.user_id)
        if owner:
            self.money = owner["points"]
        if self.money < self.item["price"]*self.amount:
            await interaction.response.send_message(embed=Embed(title="Not enough points!"))
        else:
            await self.callback(interaction, self.item, self.amount)

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def cancel(self, button: Button, interaction: Interaction):
        await interaction.response.edit_message(embed=Embed(title="Purchase canceled."), view=None)


async def confirm_purchase(interaction: Interaction, item, amount):
    """Handle successful purchase logic."""
    result = buyItem(interaction.user.id,item,amount)
    await interaction.response.send_message(embed=Embed(title=f"You bought {amount}x **{item['name']}**!"))

####################

async def sellView(interaction: discord.ApplicationContext, user_data, amount):
    inventory = user_data.get("inventory", [])
    
    if not inventory:
        await interaction.response.send_message(embed=make_embed("You have no items to sell."), ephemeral=True)
        return
    
    # Create dropdown options
    options = []
    for item in inventory:
        max_sellable = min(item["amount"], amount)
        sell_price = int(item["price"] // 1.7) * max_sellable
        
        if max_sellable > 0:
            options.append(discord.SelectOption(
                label=f"{max_sellable}x {item['name']} - {sell_price}p",
                value=item["name"]
            ))
    
    if not options:
        await interaction.response.send_message(embed=make_embed("You don't have enough items to sell."), ephemeral=True)
        return
    
    class SellDropdown(discord.ui.Select):
        def __init__(self):
            super().__init__(placeholder="Select an item to sell...", options=options)
        
        async def callback(self, sell_interaction: discord.Interaction):
            selected_item = next((item for item in inventory if item["name"] == self.values[0]), None)
            if not selected_item:
                await sell_interaction.response.send_message("Invalid item selected.", ephemeral=True)
                return
            
            max_sellable = min(selected_item["amount"], amount)
            sell_price = int(selected_item["price"] // 1.7) * max_sellable
            
            class ConfirmSell(discord.ui.View):
                def __init__(self):
                    super().__init__()
                    
                @discord.ui.button(label="Confirm Sale", style=discord.ButtonStyle.green)
                async def confirm(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                    # Perform the sale logic here (deduct items, add money)
                    result = sellItem(interaction.user.id,selected_item,sell_price,max_sellable)
                    if result == 0:
                       await interaction.response.send(
                        embed=make_embed(f"Selling failed!"), ephemeral=True
                    ) 
                    else:
                        await interaction.followup.send(
                            embed=make_embed(f"You sold {max_sellable}x {selected_item['name']} for {sell_price}p!")
                        )
                    self.stop()
                
                @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
                async def cancel(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                    await interaction.response.send("Sale canceled.", ephemeral=True)
                    self.stop()
            
            confirm_view = ConfirmSell()
            await sell_interaction.response.send_message(
                embed=make_embed(f"Are you sure you want to sell {max_sellable}x {selected_item['name']} for {sell_price}p?"),
                view=confirm_view,
                ephemeral=True
            )
    
    dropdown = SellDropdown()
    view = discord.ui.View()
    view.add_item(dropdown)
    
    await interaction.response.send_message(embed=make_embed("Select an inventory item to sell:"), view=view)
