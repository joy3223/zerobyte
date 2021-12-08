import discord, asyncio, os, random, aiohttp, datetime
from discord.ext import commands
from utils.util import return_account, cooldown_check, return_user

prefix = os.getenv("PREFIX")

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["r"])
    async def restaurant(self, ctx, user: discord.User = None):
        await cooldown_check(ctx)
        if user is None:
            userdata = await return_account(ctx.author.id)
            user = ctx.author.name
        elif user is not None:
            userdata = await return_account(user.id)
            user = user.name

        userdata = userdata[0]
        balance = userdata[1]
        employees = userdata[2]
        income = userdata[3]
        level = userdata[4]

        e = discord.Embed(title=f"{user}\'s Restaurant:", color=discord.Color.random(), timestamp=datetime.datetime.utcnow())
        e.add_field(name="Balance:", value=f"`{balance}`")
        e.add_field(name="Income:", value=f"`{income}`")
        e.add_field(name="Level:", value=f"`{level}`")
        e.add_field(name="Employees:", value=f"`{employees}`")
        e.description = f"{user}\'s Restaurant Data"
        e.set_footer(text="Values = ``")
        await ctx.send(embed = e)

    @commands.command(aliases=["w"])
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def work(self, ctx):
        acc = await return_account(ctx.author.id)
        acc = acc[0]
        employees = acc[2]
        employees = int(employees)
        level = acc[4]
        level = int(level)
        cooked = random.randint(50, 100)
        if employees != 0:
            cooked = cooked * employees
        x = (cooked * level)
        y = round(x * 7.5345345)
        add = int(acc[1]) + y
        cooktotal = int(cooked) + int(acc[3])
        await self.bot.uec.execute("UPDATE burgers SET balance = ?, income = ? WHERE user_id = ?",(add, cooktotal, ctx.author.id,),)
        await self.bot.uec.commit()
        e = discord.Embed(title="Work", timestamp=datetime.datetime.utcnow(), color=discord.Color.random())
        e.description = f"Earned - {y} \nCooked - {cooked} \nTotal - {add}"
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Economy(bot))