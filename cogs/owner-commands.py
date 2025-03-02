from datetime import datetime, timedelta
import discord
from discord.ext import commands, tasks

# Falls du fetch_profile_data nutzt, importiere es hier.
from bot_util import make_embed
from pojos.emoji_handle import app_emojis, get_emoji, get_item_emoji
from mongodb.owner import get_all_owner, get_owner, updateCheckin, updateBday, updateCheckinNotification, updateDifficulty, updateNotify
from utilities.profile import show_profile
from utilities.time import checkBdayToday, secondsUntil12h
from utilities.buy import buyView, sellView
from utilities.commands import isAOwner

subgroup = "owner_"

class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def is_in_server(self, ctx: discord.ApplicationContext):
        """Helper function to check if the command is used in a server."""
        if ctx.guild is None:
            await ctx.response.send_message(
                embed=make_embed("This command cannot be used in DMs."),
                ephemeral=True
            )
            return False
        return True

    @discord.slash_command(name=subgroup+"profile", description="Shows owner profile")
    async def profile(self, ctx: discord.ApplicationContext):
        user_data = await isAOwner(ctx.author.id,ctx)
        if not user_data:
            return
        await show_profile(ctx, user_data) 

    @discord.command(name="shop", description="Purchase an item from the marketplace.")
    async def shop(self, ctx: discord.ApplicationContext, amount: int = 1):
        if not await self.is_in_server(ctx): return  # Prevents execution in DMs

        user_data = await isAOwner(ctx.author.id,ctx)
        if not user_data:
            return
        await buyView(ctx, user_data, amount) 

    @discord.command(name="sell", description="Sells items in your inventory")
    async def sell(self, ctx: discord.ApplicationContext, amount: int = 1):
        if not await self.is_in_server(ctx): return  # Prevents execution in DMs

        user_data = await isAOwner(ctx.author.id,ctx)
        if not user_data:
            return
        await sellView(ctx, user_data, amount) 
        
    @discord.slash_command(name="check-in", description="Your daily allowance")
    async def check_in(self, ctx: discord.ApplicationContext):
        
        if not await self.is_in_server(ctx): return  # Prevents execution in DMs

        user_data = await isAOwner(ctx.author.id,ctx)
        if not user_data:
            return
        actionCategory = "check-in"
        checkin_status=0
        
        if (datetime.fromtimestamp(user_data[actionCategory]) + timedelta(hours=12))>= datetime.now():
            await ctx.response.send_message(embed=make_embed(f"Your check-in is not ready yet"), ephemeral=True)
            return
        if user_data["difficulty"]=="20min":
            checkin_status = updateCheckin(user_data["user_id"], 180)
        elif user_data["difficulty"]=="1h":
            checkin_status = updateCheckin(user_data["user_id"], 90)
        else: 
            checkin_status = updateCheckin(user_data["user_id"], 50)
        
        bday = False

        if user_data.get("bday") and checkBdayToday(user_data["bday"]):
            bday = True
            checkin_status = updateCheckin(user_data["user_id"], 50)
                
        if checkin_status == 0:  
            await ctx.response.send_message(embed=make_embed("Your Check-in didn't work."))
            return  
        
        if bday:
            await ctx.response.send_message(embed=make_embed("You checked in!\nHappy Birthday 🎂"))
        else:
            await ctx.response.send_message(embed=make_embed("You checked in!"))
        
    @discord.slash_command(name=subgroup+"bday", description="Set your Bday to get Benefits")
    async def bday(self, ctx: discord.ApplicationContext, birthday: discord.Option(input_type=str, description="Enter your Bday (MM-DD)")):
        if not await self.is_in_server(ctx): return  # Prevents execution in DMs

        user_data = await isAOwner(ctx.author.id,ctx)
        if not user_data:
            return
        
        bday = updateBday(user_data["user_id"], birthday)
        if not bday:  
            await ctx.response.send_message(embed=make_embed("Your Check-in didn't work."))
            return        
        
        await ctx.response.send_message(embed=make_embed(f"<t:{str(bday)}:F>"))
        
    @discord.slash_command(name=subgroup+"notifications", description="Sets your DM Pet Notifications")
    async def notify(self, ctx: discord.ApplicationContext, notification_type: str = discord.Option(
        description="Choose your notification setting",
        choices=["normal", "important", "none"]
    )):
        if not await self.is_in_server(ctx): 
            return  # Prevents execution in DMs

        user_data = await isAOwner(ctx.author.id,ctx)
        if not user_data:
            return
                
        # Map the notification types to specific messages
        if notification_type == "normal":
            message = "This means your pet will send you notifications in DMs about how it's doing and feels."
        elif notification_type == "important":
            message = "This means you will only receive status low and sickness notifications in DMs."
        else:  # "none"
            message = "This means your pet will no longer send you notifications in DMs."

        # Update the notification setting based on the user's choice
        result = updateNotify(user_data["user_id"], notification_type)
        if not result:  
            await ctx.response.send_message(embed=make_embed("Setting your Notifications didn't work out. Sorry."), ephemeral=True)
            return

        # Send appropriate response based on the selection
        await ctx.response.send_message(embed=make_embed(f"Your Notification setting is set to {notification_type.capitalize()}.", message))

    @discord.slash_command(name=subgroup+"difficulty", description="Sets how often your pet gets updated and sends updates")
    async def diffi(self, ctx: discord.ApplicationContext, difficulty: str = discord.Option(
        description="Choose your difficulty",
        choices=["20min", "1h", "3h"]
    )):
        if not await self.is_in_server(ctx): 
            return  # Prevents execution in DMs

        user_data = await isAOwner(ctx.author.id,ctx)
        if not user_data:
            return
                
        # Map the notification types to specific messages
        updateTime = ""
        sillyTime = ""
        if difficulty == "20min":
            updateTime="20 mins"
            sillyTime = "10 mins"
        elif difficulty == "1h":
            updateTime="1 h"
            sillyTime = "30 mins"
        else:  # "none"
            updateTime="3 h"
            sillyTime = "2 h"
            

        # Update the notification setting based on the user's choice
        result = updateDifficulty(user_data["user_id"], difficulty)
        if not result:  
            await ctx.response.send_message(embed=make_embed("Setting your Difficulty didn't work out. Sorry."), ephemeral=True)
            return

        # Send appropriate response based on the selection
        await ctx.response.send_message(embed=make_embed(f"Pet difficulty changed", f"Your pet gets updated all {updateTime} and sends you silly messages about it's idle or events all  {sillyTime}"))
    @tasks.loop(minutes=10)
    async def update_20min(self):
        owners = get_all_owner()
        for owner in owners:
            checkinResult = await secondsUntil12h(owner["check-in"])
            if checkinResult == 0 and owner.get("logs").get("check-in"):
                    user = await self.bot.fetch_user(owner["user_id"])
                    # Sending a direct message to the user
                    await user.send(embed=make_embed(":information_source: A NEW CHECK-IN IS READY"))
                    updateCheckinNotification(owner["user_id"])
def setup(bot):
    bot.add_cog(Player(bot))
