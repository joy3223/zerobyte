import discord, asyncio, os, random, aiohttp, datetime
from discord.ext import commands
from utils.util import cooldown_check

from PIL import Image, ImageFilter
from io import BytesIO

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["randomuser"])
    async def random_user(self, ctx, *, message_id):
        print("hi")
        msg = await ctx.fetch_message(message_id)
        users = []
        for reaction in msg.reactions:
            async for user in reaction.users():
                users.append(user)
        winner = random.choice(users)
        await ctx.send(f"{winner.name} has been chosen from the message.")

    @commands.command()
    async def unscramble(self, ctx):
        await cooldown_check(ctx)
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        scrambles = ["trnai#train", "appel#apple", "ptotoa#potato", "houes#house", "sneip#snipe", "burrge#burger", "caot#taco", "bacno#bacon"]
        choice = random.choice(scrambles)
        txt = choice.split("#")
        await ctx.send(f"Your goal is to unscramble the word `{txt[0]}` in under 30 seconds :) Have fun")
        m = await self.bot.wait_for("message", check=check, timeout=30)
        if m.content.lower() == str(txt[1]):
            await ctx.send("You correctly unscrambled the word!")
        else:
            await ctx.send(f"Incorrect! The correct unscramble was `{txt[1]}`")

    @commands.command()
    async def cat(self, ctx):
        await cooldown_check(ctx)
        e = discord.Embed(title="Cat!!", timestamp=datetime.datetime.utcnow(), color=discord.Color.random())
        async with aiohttp.ClientSession() as session:
            async with session.get('http://aws.random.cat/meow') as r:
                if r.status == 200:
                    js = await r.json()
        e.set_image(url=js['file'])
        e.set_footer(text=f"Requested By {ctx.author}")
        await ctx.send(embed=e)

    @commands.command()
    async def dog(self, ctx):
        await cooldown_check(ctx)
        e = discord.Embed(title="Dog!!", timestamp=datetime.datetime.utcnow(), color=discord.Color.random())
        async with aiohttp.ClientSession() as session:
            async with session.get('https://dog.ceo/api/breeds/image/random') as r:
                if r.status == 200:
                    js = await r.json()
        e.set_image(url=js['message'])
        e.set_footer(text=f"Requested By {ctx.author}")
        await ctx.send(embed=e)

    @commands.command()
    async def rip(self, ctx, user: discord.Member = None):
        await cooldown_check(ctx)
        if user is None:
            user = ctx.author
        rip = Image.open("rip.jpg")
        asset = user.avatar_url_as(size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((200,200))
        rip.paste(pfp, (165, 300))
        rip = rip.convert('RGB')
        rip.save("prip.jpg")

        e = discord.Embed(title="Rip", timestamp=datetime.datetime.utcnow(), color=discord.Color.random())
        f = discord.File("prip.jpg", filename="prip.jpg")
        e.set_image(url="attachment://prip.jpg")
        e.set_footer(text=f"Requested By {ctx.author}")
        await ctx.send(file=f, embed=e)

    @commands.command()
    async def wanted(self, ctx, user: discord.Member = None):
        await cooldown_check(ctx)
        if user is None:
            user = ctx.author
        wanted = Image.open("wanted.jpg")
        asset = user.avatar_url_as(size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((350,350))
        wanted.paste(pfp, (100, 200))
        wanted = wanted.convert("RGB")
        wanted.save("pwanted.jpg")

        e = discord.Embed(title="Wanted", color=discord.Color.random())
        f = discord.File("pwanted.jpg", filename="pwanted.jpg")
        e.set_image(url="attachment://pwanted.jpg")
        await ctx.send(file=f, embed=e)

    @commands.command(name="8ball")
    async def _8ball(self, ctx, question):
        await cooldown_check(ctx)
        laterlist = ["Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.", "Reply hazy, try again."]
        nolist = ["Very doubtful", "Don't count on it", "My reply is no.", "My sources say no", "Outlook not so good."]
        yeslist = ["Outlook good.", "Signs point to yes.", "Without a doubt.", "Yes.", "Yes - definitely", "You may rely on it.", "As I see it, yes.", "It is certain.", "It is decidedly so.", "Most likely."]
        response = random.randint(1,3)
        if response == 3:
            response = random.choice(yeslist)
        elif response == 2:
            response = random.choice(nolist)
        else:
            response = random.choice(laterlist)
        await ctx.send(f"{response}")

    @commands.command()
    async def catfact(self, ctx):
        await cooldown_check(ctx)
        async with aiohttp.ClientSession() as session:
            async with session.get("https://catfact.ninja/fact?max_length=1000") as r:
                if r.status == 200:
                    js = await r.json()
        fact = js["fact"]
        await ctx.send(f"{fact}")

    @commands.command()
    async def coinflip(self, ctx):
        await cooldown_check(ctx)
        m = await ctx.send("Flipping...")
        await asyncio.sleep(2)
        coins = ["Heads", "Tails", "Heads", "Tails", "Heads", "Tails", "Heads", "Tails", "Oops! your coin fell off the table."]
        coins = random.choice(coins)
        if coins == "Oops! your coin fell off the table.":
            await m.edit(content=f"Oops! your coin fell off the table.")
            return
        await m.edit(content=f"It landed on {coins}!")

    @commands.command()
    async def coolrate(self, ctx, user: discord.User = None):
        await cooldown_check(ctx)
        if user is None:
            user = ctx.author
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        m = await ctx.send(f"Searching for {user.name}\'s coolrate...")
        await asyncio.sleep(2)
        await m.edit(content=f"Started recieving results...")
        await asyncio.sleep(2)
        await m.edit(content=f"Recieving results complete. Processing Results...")
        await asyncio.sleep(2)
        coolrate = random.randint(1,100)
        e = random.randint(1,5)
        if e == 5:
            await m.edit(content="Uh oh! Looks like you were too cool you broke the machine!")
            return
        await m.edit(content=f"Processing results complete: \n \n{user.name}\'s Coolrate is {coolrate}")

    @commands.command()
    async def minehut(self, ctx, server):
        await cooldown_check(ctx)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.minehut.com/server/{server}?byName=true") as r:
                if r.status == 200:
                    js = await r.json()
                else:
                    await ctx.send("No server found.")
                    return
        server = js["server"]
        serverprop = server["server_properties"]

        motd = str(server["motd"])
        platform = str(server["platform"])
        name = str(server["name"])
        players = str(server["playerCount"]) + " / " + str(server["maxPlayers"])
        flight = str(serverprop["allow_flight"])
        gamemode = str(serverprop["gamemode"])
        pvp = str(serverprop["pvp"])
        status = str(server["online"])
        if status == "True":
            status = "Online"
        else:
            status = "Offline"

        e = discord.Embed(color=discord.Color.random(), title="MineHut Search:")
        e.description = f"**Information:**\n<:Error:846520463525412904> Name • {name}\n<:Error:846520463525412904> Platform • {platform}\n<:Error:846520463525412904> Gamemode • {gamemode}\n<:Error:846520463525412904> PVP • {pvp}\n<:Error:846520463525412904> Flight • {flight}\n\n**Statistics**\n<:Error:846520463525412904> Status • {status}\n<:Error:846520463525412904> Online • {players}"
        await ctx.send(embed = e)
        

def setup(bot):
    bot.add_cog(Fun(bot))