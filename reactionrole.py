import discord
import asyncio
import json
from discord.ext import commands

bot = commands.Bot(command_prefix = '!')
bot.remove_command('help') 


@bot.event
async def on_ready():
    print("Bot is ready")

@bot.command(name="selfrole")
async def self_role(ctx):
    await ctx.send("تمام این هارا در دو دقیقه جواب بدهید!")

    questions = ["پیام را وارد کنید: ", "ایموجی ها را وارد کنید: ", "رول را وارد کنید: ", "چنل را با # مشخص کنید: "]
    answers = []

    def check(user):
        return user.author == ctx.author and user.channel == ctx.channel
    
    for question in questions:
        await ctx.send(question)

        try:
            msg = await bot.wait_for('message', timeout=120.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("دفعه ی بعدی سریعتر بنویس!")
            return
        else:
            answers.append(msg.content)

    emojis = answers[1].split(" ")
    roles = answers[2].split(" ")
    c_id = int(answers[3][2:-1])
    channel = bot.get_channel(c_id)

    bot_msg = await channel.send(answers[0])

    with open("selfrole.json", "r") as f:
        self_roles = json.load(f)

    self_roles[str(bot_msg.id)] = {}
    self_roles[str(bot_msg.id)]["emojis"] = emojis
    self_roles[str(bot_msg.id)]["roles"] = roles

    with open("selfrole.json", "w") as f:
        json.dump(self_roles, f)

    for emoji in emojis:
        await bot_msg.add_reaction(emoji)

@bot.event
async def on_raw_reaction_add(payload):
    msg_id = payload.message_id

    with open("selfrole.json", "r") as f:
        self_roles = json.load(f)

    if payload.member.bot:
        return
    
    if str(msg_id) in self_roles:
        emojis = []
        roles = []

        for emoji in self_roles[str(msg_id)]['emojis']:
            emojis.append(emoji)

        for role in self_roles[str(msg_id)]['roles']:
            roles.append(role)
        
        guild = bot.get_guild(payload.guild_id)

        for i in range(len(emojis)):
            choosed_emoji = str(payload.emoji)
            if choosed_emoji == emojis[i]:
                selected_role = roles[i]

                role = discord.utils.get(guild.roles, name=selected_role)

                await payload.member.add_roles(role)
                await payload.member.send(f"شما رول  {selected_role} گرفتید!")

@bot.event
async def on_raw_reaction_remove(payload):
    msg_id = payload.message_id

    with open("selfrole.json", "r") as f:
        self_roles = json.load(f)
    
    if str(msg_id) in self_roles:
        emojis = []
        roles = []

        for emoji in self_roles[str(msg_id)]['emojis']:
            emojis.append(
                emoji)

        for role in self_roles[str(msg_id)]['roles']:
            roles.append(role)
        
        guild = bot.get_guild(payload.guild_id)

        for i in range(len(emojis)):
            choosed_emoji = str(payload.emoji)
            if choosed_emoji == emojis[i]:
                selected_role = roles[i]

                role = discord.utils.get(guild.roles, name=selected_role)

                member = await(guild.fetch_member(payload.user_id))
                if member is not None:
                    await member.remove_roles(role)


bot.run("token")