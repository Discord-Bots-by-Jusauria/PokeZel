from discord.ext import commands

@commands.command()
async def ping(ctx):
    await ctx.send(f'Hello {ctx.author.display_name}.')

async def setup(bot):
    bot.add_command(ping)