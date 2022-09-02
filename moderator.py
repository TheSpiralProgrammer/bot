import discord
import asyncio
from discord.ext import commands
import random

intents = discord.Intents.default()

intents.members = True

client = commands.Bot(command_prefix ='!', intents=intents)
client.remove_command('help') 

@client.event
async def on_ready():
        print('Bot is ready')


commands.has_permissions(kick_members=True)    
@client.command()
async def kick(ctx, Member : discord.Member, *, reason=None):
    await Member.kick(reason=reason)

@commands.has_permissions(kick_members=True)    
@client.command()
async def ban(ctx, Member : discord.Member, *, reason=None):
    await Member.ban(reason=reason)

@client.command(description="میوت کردن")
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="میوت_شده")

    if not mutedRole:
        mutedRole = await guild.create_role(name="میوت_شده")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)
    embed = discord.Embed(title="میوت شد", description=f"{member.mention} میوت شد! ", colour=discord.Colour.light_gray())
    embed.add_field(name="reason:", value=reason, inline=False)
    await ctx.send(embed=embed)
    await member.add_roles(mutedRole, reason=reason)
    await member.send(f" شما از میوت شدید: {guild.name} بخاطر: {reason}")





client.run("token")
