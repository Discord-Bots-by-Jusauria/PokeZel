import discord
from discord.ext import commands

# Falls du fetch_profile_data nutzt, importiere es hier.
from bot_util import make_embed
from pojos.emoji_handle import app_emojis, get_emoji, get_item_emoji
from services.handlerList import ALL_HANDLERS
from mongodb.owner import get_owner, updateCheckin, updateBday
from utilities.profile import show_profile
from utilities.time import checkBdayToday
from utilities.buy import buyView, sellView
subgroup = "owner_"
        
class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
   
    @discord.slash_command(name=subgroup+"profile",description="Shows owner profile")
    async def profile(self, ctx: discord.ApplicationContext):
        user_id = ctx.author.id
        user_data = get_owner(user_id=user_id)
        if not user_data:
            await ctx.response.send_message(embed=make_embed("You are not a Pet Owner"), ephemeral=True)
            return
        await show_profile(ctx,user_data) 

    @discord.command(name="shop", description="Purchase an item from the marketplace.")
    async def shop(self, ctx: discord.ApplicationContext, amount: int=1):
        user_id = ctx.author.id
        user_data = get_owner(user_id=user_id)
        if not user_data:
            await ctx.response.send_message(embed=make_embed("You are not a Pet Owner"), ephemeral=True)
            return
        await buyView(ctx,user_data,amount) 
    
    @discord.command(name="sell", description="Sells items in your inventory")
    async def sell(self, ctx: discord.ApplicationContext, amount: int=1):
        user_id = ctx.author.id
        user_data = get_owner(user_id=user_id)
        if not user_data:
            await ctx.response.send_message(embed=make_embed("You are not a Pet Owner"), ephemeral=True)
            return
        await sellView(ctx,user_data,amount) 
        
    @discord.slash_command(name="check-in",description="Your daily allowance")
    async def check_in(self, ctx: discord.ApplicationContext):
        user_id = ctx.author.id

        user_data = get_owner(user_id=user_id)
        if not user_data:
            await ctx.response.send_message(embed=make_embed("You are not a Pet Owner"), ephemeral=True)
            return
        checkin_status=0
        bday = False
        checkin_status= updateCheckin(user_id,1)
        if user_data.get("bday"):
            if checkBdayToday(user_data["bday"]):
                bday = True
                checkin_status= updateCheckin(user_id,23)
                
        if checkin_status == 0:  
            await ctx.response.send_message(embed=make_embed("Your Check-in didnt work."))
            return  
        if bday: await ctx.response.send_message(embed=make_embed("You check-in-ed\nHappy Birthday 🎂"))
        else: await ctx.response.send_message(embed=make_embed("You check-in-ed"))
        
    @discord.slash_command(name=subgroup+"bday",description="Set your Bday to get Benefits")
    async def bday(self, ctx: discord.ApplicationContext, birthday: discord.Option(input_type=str, description="Enter your Bday (MM-DD)")):
        user_id = ctx.author.id

        user_data = get_owner(user_id=user_id)
        if not user_data:
            await ctx.response.send_message(embed=make_embed("You are not a Pet Owner"), ephemeral=True)
            return
        
        bday = updateBday(user_id,birthday)
        if not bday:  
            await ctx.response.send_message(embed=make_embed("Your Check-in didnt work."))
            return        
        await ctx.response.send_message(embed=make_embed(f"<t:{str(bday)}:F>"))
def setup(bot):
    bot.add_cog(Player(bot))
