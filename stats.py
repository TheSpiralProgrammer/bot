import discord
import asyncio
from discord.ext import commands

intents = discord.Intents.default()

intents.members = True

client = commands.Bot(command_prefix ='!', intents=intents)
client.remove_command('help') 

@client.event
async def on_ready():
        print('Bot is ready')
        client.loop.create_task(stats_task())

@client.event 
async def stats_task():
   while True:
   	
      guild = client.get_guild("")
     
      member = guild.members
      boostcount = guild.premium_subscription_count
      botcount = sum(member.bot for member in guild.members)
    
      category = discord.utils.get(guild.categories, name="Server Stats")
    
      channel = category.voice_channels[1]
      await channel.edit(name=f"Members: {guild.member_count}")
      channel1 = category.voice_channels[2]
      await channel1.edit(name=f"Bots: {botcount}")
      channel2 = category.voice_channels[3]
      await channel2.edit(name=f"Boosts: {boostcount}")
      await asyncio.sleep(0)
 
	
@client.command()
async def statssetup(ctx):
  
        guild = ctx.guild
        
        if ctx.author.guild_permissions.administrator == False:
            return await ctx.send("شما دسترسی ندارید!") 
        if discord.utils.get(guild.categories, name="Server Stats"):
            return await ctx.send("استتس در این سرور وجود دارد!")
        
        member = guild.members
        boostcount = guild.premium_subscription_count
        botcount = sum(member.bot for member in guild.members)
       
        category = await guild.create_category("Server Stats") 
       
        await ctx.guild.create_voice_channel(f"Guild: {guild.name}",category=category)
        await ctx.guild.create_voice_channel(f"Members: {guild.member_count}",category=category)
        await ctx.guild.create_voice_channel(f"Bots: {botcount}",category=category) 
        await ctx.guild.create_voice_channel(f"Boosts: {boostcount}",category=category)
   
        statsimage = "https://ibb.co/drwnYXX" 
   
        embed=discord.Embed(title="📊```استتس سرور راه اندازی شد!``` 📊", description=f"{ctx.author.mention}, در سرور: **{ctx.guild}**", color=0x80FF00)
        embed.set_thumbnail(url=statsimage)
        embed.set_footer(text="")
        await ctx.send(embed=embed)
      
client.run("token")