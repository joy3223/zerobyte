import os, discord, datetime
from discord.ext import commands
from utils.util import cooldown_check

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member):
        await cooldown_check(ctx)
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send("Cannot ban a user with a higher or equal to top role then me.")
            return
        if member.top_role >= ctx.author.top_role:
            await ctx.send("That user has a higher or equal to top role then you.")
            return
        e = discord.Embed(title="SoftBan Action:", timestamp=datetime.datetime.utcnow(), color=0xff2200)
        e.description = f":white_check_mark: That user has been softbanned."
        e.add_field(name="Member:", value=f"{member}")
        e.add_field(name="Moderator:", value=f"{ctx.author}")
        e.set_footer(text="Action: SoftBan")
        await member.ban()
        await ctx.guild.unban(member)
        await ctx.send(embed = e)

    @commands.command(aliases=["purge"])
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await cooldown_check(ctx)
        if amount <= 0:
            await ctx.send("You cannot delete 0 messages")
            return
        if amount > 500:
            await ctx.send("You cannot delete more then 500 messages")
            return
        messagesdeleted = await ctx.channel.purge(limit=amount + 1, after=datetime.datetime.utcnow() - datetime.timedelta(days=13))
        deleted = len(messagesdeleted) - 1
        if deleted == 0:
            await ctx.send("I could not delete any messages.")
            return
        await ctx.send(f"Cleared {deleted} messages.", delete_after=3)

    @commands.command()
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member):
        await cooldown_check(ctx)
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send("Cannot kick a user with a higher or equal to top role then me.")
            return
        if member.top_role >= ctx.author.top_role:
            await ctx.send("That user has a higher or equal to top role then you.")
            return
        e = discord.Embed(title="Kick Action",  timestamp=datetime.datetime.utcnow(), color=0xff2200)
        e.description = f":white_check_mark: That user has been kicked."
        e.add_field(name="Member:", value=f"{member}")
        e.add_field(name="Moderator:", value=f"{ctx.author}")
        e.set_footer(text="Action: Kick")
        await member.kick()
        await ctx.send(embed = e)

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member):
        await cooldown_check(ctx)
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send("Cannot ban a user with a higher or equal to top role then me.")
            return
        if member.top_role >= ctx.author.top_role:
            await ctx.send("That user has a higher or equal to top role then you.")
            return
        e = discord.Embed(title="Ban Action:", timestamp=datetime.datetime.utcnow(), color=0xff2200)
        e.description = f":white_check_mark: That user has been banned."
        e.add_field(name="Member:", value=f"{member}")
        e.add_field(name="Moderator:", value=f"{ctx.author}")
        e.set_footer(text="Action: Ban")
        await member.ban()
        await ctx.send(embed = e)

    @commands.command(aliases=["pardon"])
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, usr: discord.User):
        await cooldown_check(ctx)
        banned_users = await ctx.guild.bans()
        try:
            member_name = usr.name
            member_disc = usr.discriminator
        except:
            e = discord.Embed(title="Member Not Found", timestamp=datetime.datetime.utcnow(), color=0xff2200)
            e.description = f":x: There is no banned user by that name. The format you should be using is: \n \nunban <user_id>"
            e.set_footer(text="Action: Error During Unban")
            await ctx.send(embed=e)
            return

        for banned_entry in banned_users:
            user = banned_entry.user

            if (user.name, user.discriminator)==(member_name, member_disc):
                await ctx.guild.unban(user)
                e = discord.Embed(title="Pardon Action:", timestamp=datetime.datetime.utcnow(), color=0x89ff45)
                e.description = f":white_check_mark: That user has been pardoned."
                e.add_field(name="Member:", value=f"{user}")
                e.add_field(name="Moderator:", value=f"{ctx.author.name}")
                e.set_footer(text="Action: Unban")
                await ctx.send(embed = e)
                return
        e = discord.Embed(title="Member Not Found", timestamp=datetime.datetime.utcnow(), color=0xff2200)
        e.description = f":x: There is no banned user by that name. The format you should be using is: \n \nunban <user_id>"
        e.set_footer(text="Action: Error During Unban")
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Moderation(bot))