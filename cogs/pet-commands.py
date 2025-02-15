import discord
from discord.ext import commands

# Falls du fetch_profile_data nutzt, importiere es hier.
from bot_util import make_embed
from pojos.emoji_handle import app_emojis, get_emoji, get_item_emoji
from utilities.profile import show_pet_profile
from mongodb.owner import get_owner
from mongodb.pet import nicknamePet
subgroup = "pet_"

class Pet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
   
    @discord.slash_command(name=subgroup+"profile",description="Shows Pet Profiles")
    async def petProfile(self, ctx: discord.ApplicationContext):
        user_id = ctx.author.id
        user_data = get_owner(user_id=user_id)
        if not user_data:
            await ctx.response.send_message(embed=make_embed("You are not a Pet Owner"), ephemeral=True)
            return
        await show_pet_profile(ctx,user_data) 
        
    @discord.slash_command(name=subgroup+"nickname",description="Name your pet :D")
    async def petNickname(self, ctx: discord.ApplicationContext, nickname:str):
        user_id = ctx.author.id
        user_data = get_owner(user_id=user_id)
        if not user_data:
            await ctx.response.send_message(embed=make_embed("You are not a Pet Owner"), ephemeral=True)
            return
        result = nicknamePet(user_id, nickname) 
        if result == 0:
            await ctx.response.send_message(embed=make_embed("Naming Failed"), ephemeral=True)
        await ctx.response.send_message(embed=make_embed("Your pet is now called "+nickname))

def setup(bot):
    bot.add_cog(Pet(bot))
