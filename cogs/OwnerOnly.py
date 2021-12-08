import os, discord, asyncio, contextlib, io, textwrap
from traceback import format_exception
from utils.util import getLink, clean_code, Pag
from discord.ext import commands

class OwnerOnly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def guilds(self, ctx):
        servers = self.bot.guilds
        for guild in servers:
            getlink = False
            if getlink == True:
                await getLink(guild)
            embed = discord.Embed(colour=0x005c87)
            embed.set_footer(text=f"Guild owned by {guild.owner}")
            embed.add_field(name=(str(guild.name)), value=str(guild.id) + "\n" + str(guild.member_count) + " members", inline=False)
            embed.set_thumbnail(url=guild.icon_url)
            await ctx.send(embed=embed)
            await asyncio.sleep(1)

    @commands.command()
    @commands.is_owner()
    async def leave(self, ctx, id=None):
        if id is None:
            id = ctx.guild.id
        guild = self.bot.get_guild(id)
        if guild is None:
            await ctx.send("I am not in a guild with that id.")
            return
        await guild.leave()
        if id != ctx.guild.id:
            await ctx.send(":white_check_mark: Left that guild.")

    @commands.command()
    @commands.is_owner()
    async def blacklist(self, ctx, user: discord.User):
        if user.id == 631290655783649320:
            await ctx.send("You cannot put my master on the blacklist!")
            return 
        usr = await self.bot.ubl.execute_fetchall(f"SELECT user_id FROM userblacklist WHERE user_id = ?", (user.id,),)
        if usr == []:
            await self.bot.ubl.execute("INSERT INTO userblacklist(user_id) VALUES(?)", (user.id,),)
            await ctx.send(f"Added {user} to the blacklist.")
        else:
            await ctx.send("That user is already blacklisted.")
            return
        await self.bot.ubl.commit()

    @commands.command()
    @commands.is_owner()
    async def unblacklist(self, ctx, user: discord.User):
        usr = await self.bot.ubl.execute_fetchall(f"SELECT user_id FROM userblacklist WHERE user_id = ?", (user.id,),)
        if usr != []:
            await self.bot.ubl.execute("DELETE FROM userblacklist WHERE user_id = ?", (user.id,),)
            await ctx.send(f"Removed {user} from blacklist")
        else:
            await ctx.send("That user is not blacklisted.")
            return
        await self.bot.ubl.commit()

    @commands.command()
    @commands.is_owner()
    async def trust(self, ctx, user: discord.User):
        usr = await self.bot.utl.execute_fetchall(f"SELECT user_id FROM usertrustlist WHERE user_id = ?", (user.id,),)
        if usr == []:
            await self.bot.utl.execute("INSERT INTO usertrustlist(user_id) VALUES(?)", (user.id,),)
            await ctx.send(f"Added {user} to the trustlist.")
        else:
            await ctx.send("That user is already trustlisted.")
            return
        await self.bot.utl.commit()

    @commands.command()
    @commands.is_owner()
    async def untrust(self, ctx, user: discord.User):
        usr = await self.bot.utl.execute_fetchall(f"SELECT user_id FROM usertrustlist WHERE user_id = ?", (user.id,),)
        if usr != []:
            await self.bot.utl.execute("DELETE FROM usertrustlist WHERE user_id = ?", (user.id,),)
            await ctx.send(f"Removed {user} from trustlist")
        else:
            await ctx.send("That user is not trustlisted.")
            return
        await self.bot.utl.commit()

    @commands.command(name="eval")
    @commands.is_owner()
    async def _eval(self, ctx, *, code):
        code = clean_code(code)

        local_variables = {
            "discord": discord,
            "commands": commands,
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message
        }

        stdout = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout):
                exec(
                    f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
                )

                obj = await local_variables["func"]()
                result = f"{stdout.getvalue()}\n-- {obj}\n"
        except Exception as e:
            result = "".join(format_exception(e, e, e.__traceback__))

        pager = Pag(
            timeout=100,
            entries=[result[i: i + 2000] for i in range(0, len(result), 2000)],
            length=1,
            prefix="```py\n",
            suffix="```"
        )

        await pager.start(ctx)

def setup(bot):
    bot.add_cog(OwnerOnly(bot))