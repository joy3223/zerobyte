import os, discord, datetime
from discord.ext import commands
from utils.util import cooldown_check

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tags(self, ctx):
        await cooldown_check(ctx)
        tags = await self.bot.tag.execute_fetchall("SELECT body FROM servertags WHERE NAME = ?",(f"{ctx.guild.id}#tags",),)
        if tags == []:
            await ctx.send("There are no tags on this server.")
            return
        tags = str(tags[0][0])
        l = ""
        for item in tags.split(","):
            if item != "":  
                l += f"{item}\n"
        e = discord.Embed(title="Server Tags:", color=discord.Color.random(), timestamp=datetime.datetime.utcnow(), description=l)
        await ctx.send(embed=e)

    @commands.command()
    async def tag(self, ctx, *, name):
        await cooldown_check(ctx)
        tag = await self.bot.tag.execute_fetchall("SELECT * FROM servertags WHERE name = ?",(f"{ctx.guild.id}#{name}",),)
        if tag == []:
            await ctx.send("That tag does not exist in this guild.")
            return
        name = tag[0][0].split("#")
        name = name[1]
        description = tag[0][1]
        e = discord.Embed(title=f"Tag: {name}", timestamp=datetime.datetime.utcnow(), color=discord.Color.random(), description=description)
        await ctx.send(embed=e)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def delete_tag(self, ctx, *, name):
        await cooldown_check(ctx)
        number = await self.bot.tag.execute_fetchall("SELECT body FROM servertags WHERE name = ?",(ctx.guild.id,),)
        if number == []:
            await ctx.send("No tags exist on this server.")
            return
        if number == "0":
            await self.bot.tag.execute("DELETE FROM servertags WHERE name = ?",(ctx.guild.id,),)
            await self.bot.tag.commit()
        t = await self.bot.tag.execute_fetchall("SELECT name FROM servertags WHERE name = ?",(f"{ctx.guild.id}#{name}",),)
        if t == []:
            await ctx.send("A tag with that name does not exist. (case insensitive)")
            return
        tags = await self.bot.tag.execute_fetchall("SELECT body FROM servertags WHERE name = ?",(f"{ctx.guild.id}#tags",),)
        if tags == []:
            await self.bot.tag.execute_fetchall("INSERT INTO servertags VALUES(?, ?)",(f"{ctx.guild.id}#tags", "",),)
            tags = await self.bot.tag.execute_fetchall("SELECT body FROM servertags WHERE name = ?",(f"{ctx.guild.id}#tags",),)
        await self.bot.tag.execute("UPDATE servertags SET body = ? WHERE name = ?",(tags[0][0].replace(f"{name}", ""), f"{ctx.guild.id}#tags",),)
        await self.bot.tag.execute("DELETE FROM servertags WHERE name = ?",(f"{ctx.guild.id}#{name}",),)
        if str(int(number[0][0]) -1) != "0":
            await self.bot.tag.execute("UPDATE servertags SET body = ? WHERE name = ?",(str(int(number[0][0]) - 1), ctx.guild.id,),)
        else:
            await self.bot.tag.execute("DELETE FROM servertags WHERE name = ?",(ctx.guild.id,),)
        await self.bot.tag.commit()
        await ctx.send("Successfully deleted that tag.")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def create_tag(self, ctx):
        await cooldown_check(ctx)
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        await ctx.send("You are about to create an tag. Type \"yes\" to continue and \"cancel\" to stop.")
        m = await self.bot.wait_for("message", check=check, timeout=30)
        if m.content.lower() == "yes":
            await ctx.send("Ok, send the name of the tag.")
        else:
            await ctx.send("Cancelled.")
            return
        name = await self.bot.wait_for("message", check=check, timeout=60)
        if len(name.content) > 200:
            await ctx.send("That title is too long. Please keep it under 200 characters.")
            return
        if name.content.lower() == "cancel":
            await ctx.send("Cancelled") 
            return
        await ctx.send("Now send the tag description text.")
        desc = await self.bot.wait_for("message", check=check, timeout=60)
        if len(desc.content) > 256:
            await ctx.send("That description is too long.")
            return
        if desc.content.lower() == "cancel":
            await ctx.send("Cancelled")
            return
        tags = await self.bot.tag.execute_fetchall("SELECT body FROM servertags WHERE name = ?",(f"{ctx.guild.id}#tags",),)
        if tags == []:
            await self.bot.tag.execute_fetchall("INSERT INTO servertags VALUES(?, ?)",(f"{ctx.guild.id}#tags", "",),)
            tags = await self.bot.tag.execute_fetchall("SELECT body FROM servertags WHERE name = ?",(f"{ctx.guild.id}#tags",),)
        number = await self.bot.tag.execute_fetchall("SELECT body FROM servertags WHERE name = ?",(ctx.guild.id,),)
        if number == []:
            await self.bot.tag.execute_fetchall("INSERT INTO servertags VALUES(?, ?)",(ctx.guild.id, 0,),)
            number = await self.bot.tag.execute_fetchall("SELECT body FROM servertags WHERE name = ?",(ctx.guild.id,),)
        if int(number[0][0]) > 9:
            await ctx.send("You have already reached the maximum tags: (10)")
            return
        t = await self.bot.tag.execute_fetchall("SELECT name FROM servertags WHERE name = ?",(f"{ctx.guild.id}#{name.content}",),)
        if t != []:
            await ctx.send("A tag with that name already exists.")
            return
        await self.bot.tag.execute("INSERT INTO servertags VALUES(?, ?)",(f"{ctx.guild.id}#{name.content}", f"{desc.content}",),)
        await self.bot.tag.execute("UPDATE servertags SET body = ? WHERE name = ?",(str(int(number[0][0]) + 1), ctx.guild.id,),)
        await self.bot.tag.execute("UPDATE servertags SET body = ? WHERE name = ?",(str(tags[0][0]) + f"{name.content},", f"{ctx.guild.id}#tags",),)
        await self.bot.tag.commit()
        e = discord.Embed(title="Created Tag:", color=discord.Color.random(), timestamp=datetime.datetime.utcnow())
        e.add_field(name="Name:", value=name.content)
        e.add_field(name="Description:", value=desc.content)
        await ctx.send(embed=e)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setwelcomechannel(self, ctx):
        await cooldown_check(ctx)
        srv = await self.bot.wgb.execute_fetchall("SELECT server_id FROM welcomegoodbye WHERE server_id = ?",(ctx.guild.id,),)
        if srv != []:
            try:
                await self.bot.wgb.execute("DELETE FROM welcomegoodbye WHERE server_id = ?",(ctx.guild.id,),)
                await self.bot.wgb.commit()
                await ctx.send(f"The welcome-goodbye message has been reset.")
            except:
                await self.bot.wgb.execute("DELETE FROM welcomegoodbye WHERE server_id = ?",(ctx.guild.id,),)
                await self.bot.wgb.commit()
                return
            return
        try:
            await ctx.send(f"The channel for welcome-goodbye messages will be set as {ctx.channel}. Yes | No")
        except:
            try:
                await ctx.author.send("The command has been cancelled because I cannot send messages in that channel.")
                return
            except:
                return
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        m = await self.bot.wait_for("message", check=check, timeout=30)
        if m.content.lower() == "yes":
            await ctx.send("Send the welcome message. Placeholders = `{mention} {serverusercount} {guildname} {userid}`")
        else:
            await ctx.send("Cancelled.")
            return
        welcome = await self.bot.wait_for("message", check=check, timeout=60)
        if welcome.content.lower() == "cancel":
            await ctx.send("Cancelled.")
            return
        else:
            await ctx.send("Send the goodbye message. Placeholders = `{username} {serverusercount} {guildname} {userid}`")
        goodbye = await self.bot.wait_for("message", check=check, timeout=60)
        if goodbye.content.lower() == "cancel":
            await ctx.send("Cancelled.")
            return
        await self.bot.wgb.execute("INSERT INTO welcomegoodbye VALUES(?, ?, ?, ?)",(ctx.guild.id, ctx.channel.id, welcome.content, goodbye.content,),)
        await self.bot.wgb.commit()
        e = discord.Embed(title="Welcome-Goodbye messages set.", timestamp=datetime.datetime.utcnow())
        e.add_field(name="Channel:", value=ctx.channel)
        e.add_field(name="Welcome Message:", value=f"{welcome.content}")
        e.add_field(name="Goodbye Message:", value=f"{goodbye.content}")
        await ctx.send(embed=e)
        

    @commands.command()
    async def embed(self, ctx):
        await cooldown_check(ctx)
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        await ctx.send("You are about to create an embed. Type \"yes\" to continue and \"cancel\" to stop.")
        m = await self.bot.wait_for("message", check=check, timeout=30)
        if m.content.lower() == "yes":
            await ctx.send("Ok, send the title of the embed.")
        else:
            await ctx.send("Cancelled.")
            return
        title = await self.bot.wait_for("message", check=check, timeout=60)
        if len(title.content) > 256:
            await ctx.send("That title is too long.")
            return
        if title.content.lower() == "cancel":
            await ctx.send("Cancelled") 
            return
        await ctx.send("Now send the description.")
        desc = await self.bot.wait_for("message", check=check, timeout=60)
        if len(desc.content) > 2048:
            await ctx.send("That description is too long.")
            return
        if desc.content.lower() == "cancel":
            await ctx.send("Cancelled")
            return
        e = discord.Embed(title=title.content, description=desc.content, timestamp=datetime.datetime.utcnow())
        e.set_footer(text=f"Embed created by {ctx.author}")
        await ctx.send(embed=e)

    @commands.command()
    async def ping(self, ctx):
        await cooldown_check(ctx)
        e = discord.Embed(title="Pong!", timestamp=datetime.datetime.utcnow(), color=0x00a6ff)
        e.description = f":ping_pong: {round(self.bot.latency * 1000)}ms"
        await ctx.send(embed=e)

    @commands.command(aliases=["pfp"])
    async def avatar(self, ctx, user: discord.Member = None):
        await cooldown_check(ctx)
        if user is None:
            username = ctx.author.name
            avatar_url = ctx.author.avatar_url
        else:
            avatar_url = user.avatar_url
            username = user.name
        e = discord.Embed(title=f"{username}\'s Profile Picture:", timestamp=datetime.datetime.utcnow(), color=0xe8431a)
        e.set_image(url=avatar_url)
        e.set_footer(text=f"Requested By {ctx.author}")
        await ctx.send(embed = e)

    @commands.command(aliases=["whois"])
    async def userinfo(self, ctx, user: discord.Member = None):
        await cooldown_check(ctx)
        if user is None:
            user = ctx.author

        roles = [role.mention for role in user.roles[1:]]
        roles.insert(0, "@everyone")
        
        embed = discord.Embed(title=f"User Info - {user}", color=0x006bb3, timestamp=datetime.datetime.utcnow())

        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}")

        embed.add_field(name="Name:", value=f"{user.name}")
        embed.add_field(name="Display Name:", value=f"{user.display_name}")
        embed.add_field(name="User ID:", value=f"{user.id}")
        
        embed.add_field(name="Created Account On:", value=user.created_at.strftime("%a, %#d %B %Y"))
        embed.add_field(name="Joined Server On:", value=user.joined_at.strftime("%a, %#d %B %Y"))

        r = ""
        for role in roles:
            r = r + f"{role} "

        embed.add_field(name="Roles:", value="".join(r))

        await ctx.send(embed=embed)

    @commands.command()
    async def serverinfo(self, ctx):
        await cooldown_check(ctx)
        text_channels = len(ctx.guild.text_channels)
        voice_channels = len(ctx.guild.voice_channels)
        categories = len(ctx.guild.categories)
        channels = text_channels + voice_channels

        embed = discord.Embed(title=f"Server Info - {ctx.guild}", color=0x006bb3, timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f"Requested by {ctx.author}")

        embed.add_field(name="Server Name:", value=f"{ctx.guild}")
        embed.add_field(name="Server Id:", value=f"{ctx.guild.id}")
        
        embed.add_field(name="Owner:", value=f"{ctx.guild.owner}")
        embed.add_field(name="Created At:", value=ctx.guild.created_at.strftime("%a, %#d %B %Y"))
        embed.add_field(name="Members:", value=f"{ctx.guild.member_count}")
        embed.add_field(name="Role Count", value=f"{len(ctx.guild.roles)}")
        
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))