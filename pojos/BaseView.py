import discord

from bot_util import make_embed

class BaseView(discord.ui.View):
    """Base View that ensures only the original user can interact and handles timeout."""
    def __init__(self, user_id, timeout=60):
        super().__init__(timeout=timeout)
        self.user_id = user_id  # Restrict to user
        self.messge = None
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Restricts interaction to the original user."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your action!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        """Disable buttons when timeout is reached."""
        for child in self.children:
            if isinstance(child, (discord.ui.Button, discord.ui.Select)):
                child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                print("Message was deleted before timeout.")


class BackButton(discord.ui.Button):
    """A reusable Back button that takes a callback function."""
    def __init__(self, user_id, label="Back",emoji = None, callback=None):
        super().__init__(label=label, style=discord.ButtonStyle.secondary,emoji=emoji)
        self.user_id = user_id
        self.callback = callback

    async def callback(self, interaction: discord.Interaction):
        """Ensures only the correct user can interact and executes callback."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("That's not yours. >:/", ephemeral=True)
            return
        if self.callback:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                print("Message was deleted before timeout.")

class AcceptButton(discord.ui.Button):
    """A reusable Back button that takes a callback function."""
    def __init__(self, user_id, label="Yes", callback=None):
        super().__init__(label=label, style=discord.ButtonStyle.green)
        self.user_id = user_id
        self.callback = callback

    async def callback(self, interaction: discord.Interaction):
        """Ensures only the correct user can interact and executes callback."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("That's not yours. >:/", ephemeral=True)
            return
        if self.callback:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                print("Message was deleted before timeout.")
class DenyButton(discord.ui.Button):
    """A reusable Back button that takes a callback function."""
    def __init__(self, user_id, label="No"):
        super().__init__(label=label, style=discord.ButtonStyle.red)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        """Ensures only the correct user can interact and executes callback."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("That's not yours. >:/", ephemeral=True)
            return
        if self.callback:
            try:
                await interaction.response.send_message(embed=make_embed("Action canceled"))
            except discord.NotFound:
                print("Message was deleted before timeout.")

class ConfirmView(BaseView):
    def __init__(self, user_id,confimActionCall):
        super().__init__(user_id= user_id)
        self.user_id = user_id  # Store user data for processing
        self.latest_message = None
        
        self.add_item(AcceptButton(self.user_id,callback=confimActionCall))
        self.add_item(DenyButton(self.user_id))  
   
class NextPageButton(discord.ui.Button):
    """Moves to the next page."""
    def __init__(self, user_id, next_callback):
        super().__init__(label="▶", style=discord.ButtonStyle.blurple)
        self.user_id = user_id
        self.next_callback = next_callback

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Not yours!", ephemeral=True)
            return
        await self.next_callback(interaction)
class PreviousPageButton(discord.ui.Button):
    """Moves to the previous page."""
    def __init__(self, user_id, previous_callback):
        super().__init__(label="◀", style=discord.ButtonStyle.blurple)
        self.user_id = user_id
        self.previous_callback = previous_callback

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Still not yours", ephemeral=True)
            return
        await self.previous_callback(interaction)


class DynamicDropdown(discord.ui.Select):
    def __init__(self, user_id, items, amount=1, placeholder="Choose an item", label_formatter=None, callback=None):
        self.label_formatter = label_formatter if label_formatter else self.default_label_formatter
        self.user_id = user_id
        self.items = items
        self.amount = amount
        self.callback = callback
        # If no custom label formatter is provided, use the default
        super().__init__(placeholder=placeholder, options=self.setUpSelection(items))
        
        
    def setUpSelection(self,items):
        options = []
        for item in items:
            label = self.label_formatter(item)  # Generate the label using the custom formatter
            options.append(discord.SelectOption(label=label, value=item['name'],description=item.get('description',"")))
        return options
    def default_label_formatter(self, item):
        """Default label format that shows item name and price multiplied by amount."""
        return f"{item['name']} - {item['price'] * self.amount}p"
    
    def changeOptions(self, items):
        self.options = self.setUpSelection(items)
    
    async def callback(self, interaction: discord.Interaction):
        """Handles the selection of an item from the dropdown."""
        selected_item_name = self.values[0]  # Get the selected value (name of the item)
        selected_item = next(item for item in self.items if item["name"] == selected_item_name)
        
        # Do something with the selected item
        await interaction.response.send_message(f"You selected {selected_item['name']} for {selected_item['price'] * self.amount} points!")
