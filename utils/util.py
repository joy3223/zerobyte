import asyncio
import discord
import aiosqlite
import os
from discord.ext.buttons import Paginator
from discord.ext import commands


class Pag(Paginator):
    async def teardown(self):
        try:
            await asyncio.sleep(0.25)
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass

def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content

async def return_account(user_id):
    db = await aiosqlite.connect("burgers.db")
    tf = await db.execute_fetchall("SELECT user_id FROM burgers WHERE user_id = ?",(user_id,),)
    if tf == []:
        await db.execute("INSERT INTO burgers(user_id, balance, employees, income, level) VALUES(?,?,?,?,?)",(user_id, 10000, 0, 0, 1),)
        data = await db.execute_fetchall("SELECT * FROM burgers WHERE user_id = ?",(user_id,),)
        datalist = data
        await db.commit()
    else:
        data = await db.execute_fetchall("SELECT * FROM burgers WHERE user_id = ?",(user_id,),)
        datalist = data
    await db.close()
    return datalist

async def get_prefix(bot, message):
    prefix = await bot.scf.execute_fetchall("SELECT prefix FROM serverconfig WHERE server_id = ?",(message.guild.id,),)
    if prefix == []:
        await bot.scf.execute("INSERT INTO serverconfig(server_id, prefix) VALUES(?,?)",(message.guild.id, ">",),)
        await bot.scf.commit()
        prefix = await bot.scf.execute_fetchall("SELECT prefix FROM serverconfig WHERE server_id = ?",(message.guild.id,),)
    return prefix[0][0]

async def getLink(guild):
    link = await guild.text_channels[0].create_invite()
    print(link)

_cd = commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.member)

userids = ["631290655783649320"]

async def cooldown_check(ctx):
    if str(ctx.author.id) in userids:
        return
    bucket = _cd.get_bucket(ctx.message)
    retry_after = bucket.update_rate_limit()
    if retry_after:
        raise commands.CommandOnCooldown(bucket, retry_after)
    return True

async def return_channel(bot, channel_id):
    chnl = bot.get_channel(channel_id)
    if chnl is None:
        try:
            chnl = await bot.fetch_channel(channel_id)
        except:
            return None
    return chnl

async def return_guild(bot, guild_id):
    guild = bot.get_guild(guild_id)
    if guild is None:
        try:
            guild = await bot.fetch_guild(guild_id)
        except:
            return None
    return guild

async def return_user(bot, user_id):
    user = bot.get_user(user_id)
    if user is None:
        try:
            user = await bot.fetch_user(user_id)
        except:
            return None
    return user