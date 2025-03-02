import discord

from bot_util import make_embed
from pojos.BaseView import BaseView, NextPageButton, PreviousPageButton

def correctEmbedText(index):
    if index == 0: ## Introduction
        embed = make_embed("Pointlink Petshop Guide","Welcome to PointLink pet guide. Here you figure out, how to adopt a pet. How to take care of it. Features and secrets.\n Let's hope you read all.\n-# If features mentioned don't work, please inform Jusauria\n## Starting")
        embed.add_field(name="Adoption", value="To adopt a pet use `/adopt`. The options of adopting is a lot. So think about which one you like the most.", inline=False)
        embed.add_field(name="Check-in 12h", value="At the beginning you probably don't have any points. `/check-in` gives you every 12h enough points to make sure your pet will stay alive. Even so it will send you notification when the next one is ready, if not set otherwise.", inline=False)
        embed.add_field(name="Shop", value="For buying items your pet needs.", inline=False)
        return embed

    if index == 1: ## Owner commands
        embed = make_embed("Owner Commands","All owner related commands start with /owner_")
        embed.add_field(name="bday", value="Set your Birthday to get extra benefits, like more points in `/check-in`", inline=False)
        embed.add_field(name="difficulty", value="Choose between 20min, 1h, 3h intervals of pet updates. The update rate predicts how long your pet will survive with no interactions. -# Default is 1h", inline=False)
        embed.add_field(name="notifications", value="Choose between normal, important, none. Important only gives you low stat mood change and dying messages. None will never give you any.", inline=False)
        embed.add_field(name="profile", value="Check details about your player like points, inventory, settings.", inline=False)
        return embed

    if index == 2: ## Pet commands
        embed = make_embed("Pet Commands", "All owner related commands start with /pet")
        embed.add_field(name="nickname", value="There's no limit to naming your pet. Go ahead.", inline=False)
        embed.add_field(name="attention", value="Pat, Cuddle, ... for regaining happiness", )
        embed.add_field(name="drench", value="Pouring down water it's throat to satisfy thirst!", )
        embed.add_field(name="feed", value="Force it to eat 99 pieces of Stale bread to satisfy hunger!", )
        embed.add_field(name="sleep", value="Turn it into a burrito until it falls asleep to regain energy!",)
        embed.add_field(name="offer", value="Give your pet items like medicine to solve its sicknesses.", inline=False)
        return embed

    if index == 3: ## Mechanics
        embed = make_embed("Mechanics", "More Details how everything works.")
        embed.add_field(name="Personality", value="Each pet gets a random personality assigned. These personalities influence emotions they feel when sick or low, how long some last, how often some occur, what actions they have a chance to refuse, and which they like more than others.", inline=False)
        embed.add_field(name="Emotions/Moods", value="Until now emotions are just a silly gimmick that have the chance of changing output texts. They will have more features in the future.", inline=False)
        embed.add_field(name="Updates", value="Updates depend on your difficulty.\nEach update the stats go down. When your pet gets 0 on Hunger, Thirst, or Health, it gets the Sickness 'Dying'. When you don't solve the stat in a 30-minute timeframe, your pet will die. Happiness and Intelligence on 0 do not affect the pet but give negative moods. 0 Energy makes your pet faint, but you lose 50% of Happiness. Your Pet can only lose health when it's sick. It's recommended to remove sicknesses as fast as you can.", inline=False)
        embed.add_field(name="Sleeping", value="By default your pet will only regain energy when sleeping. But with the item 'Blanket' in the inventory, it will regain happiness too, as you put it on them when they sleep.", inline=False)
        embed.add_field(name="Evolutions", value=":D", )
        embed.add_field(name="Jobs", value=":D",)
        embed.add_field(name="Level", value=":D", )
        return embed


class HelpView(BaseView):
    def __init__(self, user_id):
        super().__init__(user_id,timeout=120)
        self.current_index = 0
        self.previous_page_button = PreviousPageButton(self.user_id, self.previous_page)
        self.next_page_button = NextPageButton(self.user_id, self.next_page)
        
        self.add_item(self.previous_page_button)
        self.add_item(self.next_page_button)
    
    
    async def update_shop(self, interaction: discord.Interaction):
       
        self.update_buttons()
        embed = correctEmbedText(self.current_index)

        await interaction.response.edit_message(embed=embed, view=self)
        
    def update_buttons(self):
        """Update navigation buttons' state."""
        self.previous_page_button.disabled = self.current_index == 0
        self.next_page_button.disabled = self.current_index == 3
    async def previous_page(self, interaction: discord.Interaction):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_buttons()
            await self.update_shop(interaction)
    async def next_page(self, interaction: discord.Interaction):
            self.current_index += 1
            self.update_buttons()
            await self.update_shop(interaction)

async def helpView(interaction: discord.ApplicationContext):
    view = HelpView(interaction.author.id)
    await interaction.response.send_message(embed=correctEmbedText(0),view=view)