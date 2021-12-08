import discord, asyncio, os, random, aiohttp, datetime
from discord.ext import commands

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        e = discord.Embed(color=0xbf3300)
        e.set_author(name=f"{ctx.author.name}", url=f"https://discord.com/users/{ctx.author.id}", icon_url=f"{ctx.author.avatar_url}")
        e.timestamp = datetime.datetime.utcnow()
        if isinstance(error, commands.errors.MissingRequiredArgument):
            e.description = f"<:Error:846520463525412904> Command is missing argument(s) that are required."
            await ctx.send(embed=e)
        elif isinstance(error, commands.errors.MemberNotFound):
            e.description = f"<:Error:846520463525412904> There is no user by that given/mentioned name."
            await ctx.send(embed=e)
        elif isinstance(error, commands.errors.CommandNotFound):
            return
        elif isinstance(error, commands.errors.CommandOnCooldown):
            time = 0
            if error.retry_after > 59:
                time = str(round((error.retry_after / 60), 2))
                time += "m"
            if error.retry_after > 3599:
                time = str(round((error.retry_after / 3600), 2))
                time += "h"
            if error.retry_after > 86399:
                time = str(round((error.retry_after / 86400), 2))
                time += "d"
            if error.retry_after < 60:
                time = str(round(error.retry_after, 1))
                time += "s"
            e.description = f"<:Error:846520463525412904> The run command is on cooldown. Please try again after `{time}`"
            await ctx.send(embed=e)
        elif isinstance(error, commands.errors.BadArgument):
            e.description = f"<:Error:846520463525412904> That command recieved a argument that was not correct. Please check on the usage and try again."
            await ctx.send(embed=e)
        elif isinstance(error, commands.MissingPermissions):
            e.description = f"<:Error:846520463525412904> You do not have the required permissions to run that command."
            await ctx.send(embed=e)
        elif isinstance(error, commands.BotMissingPermissions):
            e.description = f"<:Error:846520463525412904> I do not have the permissions to run that command. Please give me the permission(s) {' '.join(error.missing_perms)} and try again."
            await ctx.send(embed=e)
        elif isinstance(error, commands.errors.NotOwner):
            e.description = f"<:Error:846520463525412904> That command is strictly permitted to owner only."
            await ctx.send(embed=e)
        elif isinstance(error, commands.errors.CommandInvokeError):
            if str(error) == "Command raised an exception: TimeoutError: ":
                e.description = f"<:Error:846520463525412904> The user did not respond in time."
                await ctx.send(embed=e)
            elif str(error) == "Command raised an exception: Forbidden: 403 Forbidden (error code: 50013): Missing Permissions":
                return
            else:
                raise error
        else:
            raise error

def setup(bot):
    bot.add_cog(Errors(bot))