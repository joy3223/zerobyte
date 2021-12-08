import os, discord, datetime
from discord.ext import commands
from utils.util import get_prefix, cooldown_check

class ServerConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["set_prefix"])
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx, *, prefix):
        await cooldown_check(ctx)
        oldprefix = await get_prefix(self.bot, ctx)
        if oldprefix == prefix:
            await ctx.send("I\'m already listening for that prefix")
            return
        if prefix.lower() == "reset" and oldprefix == ">":
            await ctx.send("I\'m already listening for that prefix")
            return
        if prefix.lower() == "reset":
            await self.bot.scf.execute("UPDATE serverconfig SET prefix = ? WHERE server_id = ?",(">", ctx.guild.id,),)
            e = discord.Embed(title="Prefix Updated:", timestamp=datetime.datetime.utcnow(), color=0xffc400)
            e.add_field(name="Old Prefix:", value=f"{oldprefix}")
            e.add_field(name="New Prefix:", value=f">")
            e.set_footer(text="Your prefix has been reset")
            await ctx.send(embed=e)
            await self.bot.scf.commit()
            return
        if len(prefix) > 8:
            await ctx.send("You cannot have a prefix longer then 8 characters.")
            return
        if "@here" in prefix:
            await ctx.send("You cannot have a prefix that has a here mention in it.")
            return
        if "@everyone" in prefix:
            await ctx.send("You cannot have a prefix that has a everyone mention in it.")
            return
        await self.bot.scf.execute("UPDATE serverconfig SET prefix =? WHERE server_id = ?",(prefix, ctx.guild.id,),)
        e = discord.Embed(title="Prefix Updated:", timestamp=datetime.datetime.utcnow(), color=0xffc400)
        e.add_field(name="Old Prefix:", value=f"{oldprefix}")
        e.add_field(name="New Prefix:", value=f"{prefix}")
        e.set_footer(text="Your prefix has been changed")
        await ctx.send(embed=e)
        await self.bot.scf.commit()

def setup(bot):
    bot.add_cog(ServerConfig(bot))