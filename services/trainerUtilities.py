from collections import defaultdict
import discord

from bot_util import make_embed
from mongodb.owner import get_owner
from pojos.emoji_handle import get_emoji


class ProfileView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)  # Persistent view
        self.user_id = user_id

    @discord.ui.button(label="Inventory", style=discord.ButtonStyle.primary, custom_id="profile_view:inventory")
    async def inventory_button(self, button: discord.Button, interaction: discord.Interaction):
        """Callback for the Inventory button on the Profile page."""
        await show_inventory(interaction, self.user_id)


class InventoryView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)  # Persistent view
        self.user_id = user_id

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary, custom_id="inventory_view:back")
    async def back_button(self, button: discord.Button, interaction: discord.Interaction):
        """Callback for the Back button on the Inventory page."""
        await show_profile(interaction, self.user_id)


async def show_profile(interaction: discord.Interaction, user_id: int):
    """
    Displays the trainer's profile with an Inventory button.
    
    Parameters:
    - interaction: The interaction triggering this function.
    - user_id: The unique ID of the trainer.
    """
    # Fetch user data
    data = get_owner(user_id)
    if not data:
        await interaction.followup.send(embed=make_embed("No Trainer Found"), ephemeral=True)
        return

    # Create Profile Embed
    embed = make_embed(title=data['name'], description="")

    # Set Thumbnail
    if interaction.user.avatar:
        embed.set_thumbnail(url=interaction.user.avatar.url)
    else:
        embed.set_thumbnail(url=interaction.user.default_avatar.url)

    # Add Fields
    embed.add_field(name="Trainer-Level", value=data.get("trainer_lvl", "N/A"), inline=True)
    embed.add_field(name="Role", value=data.get("role", "N/A"), inline=True)
    embed.add_field(name="PokeDollar", value=data.get("dollar", "0"), inline=True)
    embed.add_field(name="Favorite", value=data.get("fav", "None"), inline=False)
    embed.add_field(name="Dex filled", value=str(data.get("dex_filled", 0)), inline=True)
    embed.add_field(name=":sparkles: Shiny", value=str(data.get("shiny_count", 0)), inline=True)

    # Team Display
    stringTeam = ""
    for pokemon in data.get("team", []):
        shiny_star = ":sparkles:" if pokemon.get("is_shiny", False) else ""
        stringTeam += f"lvl {pokemon.get('lvl', 1)} {get_emoji(pokemon.get('name', 'unknown'))} {shiny_star} {pokemon.get('nickname', 'No Name')}\n"
    embed.add_field(name="Team", value=stringTeam or "No Pokémon in team.", inline=False)

    embed.add_field(name="Passive Training", value=str(data.get("passive", 0)), inline=False)
    embed.add_field(name="Badges", value=data.get("badges", "None"), inline=False)
    embed.add_field(name="Started", value=f"<t:{str(data.get('started', 0))}:F>", inline=False)

    # Create and attach ProfileView
    view = ProfileView(user_id=user_id)

    # Send or Edit Message
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def show_inventory(interaction: discord.Interaction, user_id: int):
    """
    Displays the trainer's inventory with a Back button.
    
    Parameters:
    - interaction: The interaction triggering this function.
    - user_id: The unique ID of the trainer.
    """
    # Fetch user data
    data = get_owner(user_id)
    if not data:
        await interaction.followup.send(embed=make_embed("No Trainer Found"), ephemeral=True)
        return

    # Assume 'inventory' is a dictionary with categories as keys and list of items as values
    inventory = data.get('inventory', {})

    # Create Inventory Embed
    embed = make_embed(title="Inventory", description="")

    if not inventory:
        embed.add_field(name="Inventory", value="No items in inventory.", inline=False)
    else:
        # Step 1: Group items by category
        category_dict = defaultdict(list)
        for item in inventory:
            category = item.get('category', 'Uncategorized')  # Default to 'Uncategorized' if category is missing
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
                quantity = item.get('quantity', 1)  # Default quantity to 1 if not specified
                cost = item.get('cost', 0)
                short_text = item.get('shortText', '')
                # You can customize the format as needed
                line = f"**{name}** x{quantity} - ${(cost/2)}\n_{short_text}_"
                item_lines.append(line)
            
            # Join all item lines into a single string separated by newlines
            item_list = "\n\n".join(item_lines)
            
            # Add the category and its items as a field in the embed
            embed.add_field(name=category.capitalize(), value=item_list, inline=True)

    # Create and attach InventoryView
    view = InventoryView(user_id=user_id)

    # Edit the original message with the Inventory embed and view
    await interaction.response.edit_message(embed=embed, view=view)
