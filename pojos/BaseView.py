import discord
from discord.ext import commands

from bot_util import make_embed

class BaseView(discord.ui.View):
    """Base class to handle interaction validation and timeout behavior."""
    def __init__(self, user_id, timeout=60):
        super().__init__(timeout=timeout)
        self.user_id = user_id  # Restrict to user

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allow the user who initiated the view to interact."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(embed=make_embed( "Slow down a bit. That's not your window."), ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        """Disable buttons on timeout."""
        for child in self.children:
            if isinstance(child, (discord.ui.Button, discord.ui.Select)):
                child.disabled = True
        await self.message.edit(view=self)


class ItemSelectionView(BaseView):
    """Generalized view for selecting and using items."""
    def __init__(self, user_id, pet, items, category, callback):
        super().__init__(user_id)
        self.pet = pet
        self.items = items
        self.category = category
        self.callback = callback  # Function to execute on selection

        options = [
            discord.SelectOption(label=f"{item['name']} ({item['filling']})", value=item["name"])
            for item in items
        ]
        
        self.select_menu = discord.ui.Select(
            placeholder=f"Select {category}",
            options=options
        )
        self.select_menu.callback = self.select_item
        self.add_item(self.select_menu)

    async def select_item(self, interaction: discord.Interaction):
        """Handles item selection and calls the provided callback."""
        selected_item = next(item for item in self.items if item["name"] == self.select_menu.values[0])
        await self.callback(interaction, self.pet, selected_item)
