import os, discord, sys, aiosqlite, asyncio, dotenv, datetime, psutil
from discord.ext import commands, tasks
from utils.util import get_prefix, cooldown_check, return_channel, return_user

intents = discord.Intents.default()  
intents.members = True

dotenv.load_dotenv()
token = os.getenv('TOKEN2')
prefix = os.getenv('PREFIX')

bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents, allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False))
bot.prefix = prefix

# Sqlite

loop = asyncio.get_event_loop()
bot.ubl = loop.run_until_complete(aiosqlite.connect('userblacklist.db'))
bot.scf = loop.run_until_complete(aiosqlite.connect('serverconfig.db'))
bot.uec = loop.run_until_complete(aiosqlite.connect('burgers.db'))
bot.utl = loop.run_until_complete(aiosqlite.connect('usertrustlist.db'))
bot.wgb = loop.run_until_complete(aiosqlite.connect('welcomegoodbye.db'))
bot.tag = loop.run_until_complete(aiosqlite.connect('servertags.db'))
bot.timestarted = datetime.datetime.utcnow()

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    await bot.ubl.execute("CREATE TABLE IF NOT EXISTS userblacklist(user_id TEXT)")
    await bot.scf.execute("CREATE TABLE IF NOT EXISTS serverconfig(server_id TEXT, prefix TEXT)")
    await bot.uec.execute("CREATE TABLE IF NOT EXISTS burgers(user_id TEXT, balance TEXT, employees TEXT, income TEXT, level TEXT)")
    await bot.utl.execute("CREATE TABLE IF NOT EXISTS usertrustlist(user_id TEXT)")
    await bot.wgb.execute("CREATE TABLE IF NOT EXISTS welcomegoodbye(server_id TEXT, channel_id TEXT, welcome TEXT, goodbye TEXT)")
    await bot.tag.execute("CREATE TABLE IF NOT EXISTS servertags(name TEXT, body TEXT)")
    print("-----")
    print(f"Logged in as {str(bot.user)}")

@tasks.loop(seconds=120)
async def botstatus():
    await bot.wait_until_ready()
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=">Help | @Zer0Byte"))
    await asyncio.sleep(60)
    await bot.change_presence(status = discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{str(len(bot.guilds))} guilds."))

@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.channel.DMChannel):
        return
    if message.author.bot:
        return
    mention = f'<@!{bot.user.id}>'
    mention2 = f'<@{bot.user.id}>'
    prefix2 = await get_prefix(bot, message)
    if message.content.startswith(mention):
        e = discord.Embed(title="Mentioned", timestamp=datetime.datetime.utcnow(), color=0x32a88b)
        e.description = f"My Prefix for this server is: **{prefix2}**"
        await message.channel.send(embed=e)
    elif message.content.startswith(mention2):
        e = discord.Embed(title="Mentioned", timestamp=datetime.datetime.utcnow(), color=0x32a88b)
        e.description = f"My Prefix for this server is: **{prefix2}**"
        await message.channel.send(embed=e)
    if message.content.startswith(f"{prefix2}"):
        b = await bot.ubl.execute_fetchall("SELECT user_id FROM userblacklist WHERE user_id = ?",(message.author.id,),)
        if b != []:
            return
    await bot.process_commands(message)

@bot.event
async def on_guild_remove(guild):
    rows = await bot.scf.execute_fetchall("SELECT prefix FROM serverconfig WHERE server_id = ?", (guild.id,),)
    if rows == []:
        return
    else:
        await bot.scf.execute("DELETE FROM serverconfig WHERE server_id = ?", (guild.id,),)
        owner = await return_user(bot, 631290655783649320)
        e = discord.Embed(title="Left Guild")
        e.description = f"Guild Name - {guild.name}\nGuild ID - {guild.id}\n\nOwner - {guild.owner}" 
        e.timestamp = datetime.datetime.utcnow()
        await owner.send(embed = e)  
    rows2 = await bot.wgb.execute_fetchall("SELECT server_id FROM welcomegoodbye WHERE server_id = ?",(guild.id,),)
    if rows2 == []:
        return
    else:
        await bot.wgb.execute("DELETE FROM welcomgoodbye WHERE server_id = ?",(guild.id,),)

@bot.event
async def on_guild_join(guild):
    owner = await return_user(bot, 631290655783649320)
    e = discord.Embed(title="Joined Guild")
    e.description = f"Guild Name - {guild.name}\nGuild ID - {guild.id} \nGuild Members - {len(guild.members)}\n\nOwner - {guild.owner}"
    e.timestamp = datetime.datetime.utcnow()
    await owner.send(embed = e)

@bot.event
async def on_member_join(member):
    if member.id == 814253004474679356:
        return
    srv = await bot.wgb.execute_fetchall("SELECT server_id FROM welcomegoodbye WHERE server_id = ?",(member.guild.id,),)
    if srv == []:
        return
    channel = await bot.wgb.execute_fetchall("SELECT channel_id FROM welcomegoodbye WHERE server_id = ?",(member.guild.id,),)
    channel = await return_channel(bot, channel[0][0])
    if channel is None:
        await bot.wgb.execute("DELETE FROM welcomegoodbye WHERE server_id = ?",(member.guild.id,),)
        await bot.wgb.commit()
        return
    welcomemsg = await bot.wgb.execute_fetchall("SELECT welcome FROM welcomegoodbye WHERE server_id = ?",(member.guild.id,),)
    welcomemsg = welcomemsg[0][0]
    welcomemsg = welcomemsg.replace("{mention}", f"<@{member.id}>")
    welcomemsg = welcomemsg.replace("{serverusercount}", f"{len(member.guild.members)}")
    welcomemsg = welcomemsg.replace("{guildname}", f"{member.guild.name}")
    welcomemsg = welcomemsg.replace("{userid}", f"{member.id}")
    try:
        await channel.send(f"{welcomemsg}")
    except discord.Forbidden:
        await bot.wgb.execute("DELETE FROM welcomegoodbye WHERE server_id = ?",(member.guild.id,),)
        await bot.wgb.commit()

@bot.event
async def on_member_remove(member):
    if member.id == 814253004474679356:
        return
    srv = await bot.wgb.execute_fetchall("SELECT server_id FROM welcomegoodbye WHERE server_id = ?",(member.guild.id,),)
    if srv == []:
        return
    channel = await bot.wgb.execute_fetchall("SELECT channel_id FROM welcomegoodbye WHERE server_id = ?",(member.guild.id,),)
    channel = await return_channel(bot, channel[0][0])
    if channel is None:
        await bot.wgb.execute("DELETE FROM welcomegoodbye WHERE server_id = ?",(member.guild.id,),)
        await bot.wgb.commit()
        return
    goodbyemsg = await bot.wgb.execute_fetchall("SELECT goodbye FROM welcomegoodbye WHERE server_id = ?",(member.guild.id,),)
    goodbyemsg = goodbyemsg[0][0]
    goodbyemsg = goodbyemsg.replace("{username}", f"{member.name}")
    goodbyemsg = goodbyemsg.replace("{serverusercount}", f"{len(member.guild.members)}")
    goodbyemsg = goodbyemsg.replace("{guildname}", f"{member.guild.name}")
    goodbyemsg = goodbyemsg.replace("{userid}", f"{member.id}")
    try:
        await channel.send(f"{goodbyemsg}")
    except discord.Forbidden:
        await bot.wgb.execute("DELETE FROM welcomegoodbye WHERE server_id = ?",(member.guild.id,),)
        await bot.wgb.commit()

class MyHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        await cooldown_check(self.context)
        prefix = await get_prefix(bot, self.context)
        destination = self.get_destination()
        e = discord.Embed(title="Help:", color=discord.Color.random(), description="", timestamp=datetime.datetime.utcnow())
        for page in self.paginator.pages:
            e.description += page
        e.add_field(name="Prefix:", value=f"{prefix}")
        e.add_field(name="Links:", value="[Default Invite Link](https://discord.com/api/oauth2/authorize?client_id=814253004474679356&permissions=0&scope=bot) \n[Official Support Discord](https://discord.gg/VKqY2nk6N3)")
        e.set_footer(text="<Required Argument> [Unrequired Argument]")
        await destination.send(embed=e)

bot.help_command = MyHelpCommand()

@bot.command()
async def info(ctx):
    await cooldown_check(ctx)
    e = discord.Embed(color=discord.Color.random(), timestamp=datetime.datetime.utcnow())
    owner = await return_user(bot, 631290655783649320)
    delta_uptime = datetime.datetime.utcnow() - bot.timestarted
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    uptime = f"{days}d, {hours}h, {minutes}m, {seconds}s"
    ram = psutil.virtual_memory()
    process = psutil.Process(os.getpid())
    ram = process.memory_info().rss
    ram = str(round(int(ram) / 1000000))
    ram += " MB"
    e.description = f"Zer0Byte is a userfriendly discord bot that can do image manipulation, moderation, fun and useful commands. \n[Invite Link](https://discord.com/api/oauth2/authorize?client_id=814253004474679356&permissions=0&scope=bot) • [Bot Support Discord](https://discord.gg/VKqY2nk6N3) \n\n**Information:** \n<:Arrow:846520501291581441> **Developer •** [{owner}](https://discord.com/users/631290655783649320) \n<:Arrow:846520501291581441> **Library •** discord.py {discord.__version__} \n<:Arrow:846520501291581441> **Creation Date •** 24 February 2021 \n \n**Statistics:** \n<:Arrow:846520501291581441> **Servers •** {len(bot.guilds)} \n<:Arrow:846520501291581441> **Uptime •** {uptime} \n<:Arrow:846520501291581441> **RAM Usage •** {ram} \n<:Arrow:846520501291581441> **API Latency •** {round(bot.latency * 1000)}ms"
    e.set_author(name="Zer0Byte", icon_url="https://cdn.discordapp.com/avatars/814253004474679356/51bfffb4bd929dac0889407f67331861.png?size=256", url=f"https://discord.com/users/814253004474679356")
    await ctx.send(embed=e)

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")
        print(f"Loaded {filename[:-3]}")

botstatus.start()
bot.run(token)