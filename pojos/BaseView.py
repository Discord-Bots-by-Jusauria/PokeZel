import discord

class BaseView(discord.ui.View):
    """Base View that ensures only the original user can interact and handles timeout."""
    def __init__(self, user_id, timeout=60):
        super().__init__(timeout=timeout)
        self.user_id = user_id  # Restrict to user

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Restricts interaction to the original user."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your interaction!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        """Disable buttons when timeout is reached."""
        for child in self.children:
            if isinstance(child, (discord.ui.Button, discord.ui.Select)):
                child.disabled = True
        await self.message.edit(view=self)


class BackButton(discord.ui.Button):
    """A reusable Back button that takes a callback function."""
    def __init__(self, user_id, label="Back", callback=None):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.user_id = user_id
        self.callback = callback

    async def callback(self, interaction: discord.Interaction):
        """Ensures only the correct user can interact and executes callback."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("That's not yours. >:/", ephemeral=True)
            return
        if self.callback:
            await self.callback(interaction)


class NextPageButton(discord.ui.Button):
    """Moves to the next page."""
    def __init__(self, user_id, next_callback):
        super().__init__(label="Next", style=discord.ButtonStyle.primary)
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
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)
        self.user_id = user_id
        self.previous_callback = previous_callback

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Still not yours", ephemeral=True)
            return
        await self.previous_callback(interaction)
