import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import json
import asyncio

bot = commands.Bot(command_prefix="!")
bot.remove_command("help")

@bot.event
async def on_ready():
    print("Bot is ready")


@bot.command()
async def newticket(ctx, *, args = None):

    await bot.wait_until_ready()

    if args == None:
        message_content = "لطفا صبر کنید تا ادمین ها جواب شما را بدهند!"
    
    else:
        message_content = "".join(args)

    with open("data.json") as f:
        data = json.load(f)

    ticket_number = int(data["ticket-counter"])
    ticket_number += 1

    ticket_channel = await ctx.guild.create_text_channel("ticket-{}".format(ticket_number))
    await ticket_channel.set_permissions(ctx.guild.get_role(ctx.guild.id), send_messages=False, read_messages=False)

    for role_id in data["valid-roles"]:
        role = ctx.guild.get_role(role_id)

        await ticket_channel.set_permissions(role, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
    
    await ticket_channel.set_permissions(ctx.author, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)

    em = discord.Embed(title="تیکتی جدید از: {}#{}".format(ctx.author.name, ctx.author.discriminator), description= "{}".format(message_content), color=0x00a8ff)

    await ticket_channel.send(embed=em)

    pinged_msg_content = ""
    non_mentionable_roles = []

    if data["pinged-roles"] != []:

        for role_id in data["pinged-roles"]:
            role = ctx.guild.get_role(role_id)

            pinged_msg_content += role.mention
            pinged_msg_content += " "

            if role.mentionable:
                pass
            else:
                await role.edit(mentionable=True)
                non_mentionable_roles.append(role)
        
        await ticket_channel.send(pinged_msg_content)

        for role in non_mentionable_roles:
            await role.edit(mentionable=False)
    
    data["ticket-channel-ids"].append(ticket_channel.id)

    data["ticket-counter"] = int(ticket_number)
    with open("data.json", 'w') as f:
        json.dump(data, f)
    
    created_em = discord.Embed(title="تیکت شما درست شد در: {}".format(ticket_channel.mention), color=0x00a8ff)
    
    await ctx.send(embed=created_em)

@bot.command()
async def closeticket(ctx):
    with open('data.json') as f:
        data = json.load(f)

    if ctx.channel.id in data["ticket-channel-ids"]:

        channel_id = ctx.channel.id

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() == "close"

        try:

            em = discord.Embed(title="بستن تیکت", description="آیا اطمینان دارید که تیکت خود را ببندید؟ اگر اطمینان دارید بنویسید :close", color=0x00a8ff)
        
            await ctx.send(embed=em)
            await bot.wait_for('message', check=check, timeout=60)
            await ctx.channel.delete()

            index = data["ticket-channel-ids"].index(channel_id)
            del data["ticket-channel-ids"][index]

            with open('data.json', 'w') as f:
                json.dump(data, f)
        
        except asyncio.TimeoutError:
            em = discord.Embed(title="تمام شدن وقت", description="وقت شما تمام شد لطفا بار دیگر امتحان کنید!", color=0x00a8ff)
            await ctx.send(embed=em)

        

@bot.command()
async def addaccess(ctx, role_id=None):

    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if valid_user or ctx.author.guild_permissions.administrator:
        role_id = int(role_id)

        if role_id not in data["valid-roles"]:

            try:
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                data["valid-roles"].append(role_id)

                with open('data.json', 'w') as f:
                    json.dump(data, f)
                
                em = discord.Embed(title="اد شدن رول", description="شما رول `{}` را به لیست اضافه کردید".format(role.name), color=0x00a8ff)

                await ctx.send(embed=em)

            except:
                em = discord.Embed(title="رول اشتباه است", description="رول شما اشتباه است")
                await ctx.send(embed=em)
        
        else:
            em = discord.Embed(title="اکسس داشتن", description="این رول به تیکت اکسس دارد!", color=0x00a8ff)
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="نداشتن پرمیشن", description="ببخشید شما پرمیشن کافی ندارید!", color=0x00a8ff)
        await ctx.send(embed=em)

@bot.command()
async def delaccess(ctx, role_id=None):
    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass

    if valid_user or ctx.author.guild_permissions.administrator:

        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            valid_roles = data["valid-roles"]

            if role_id in valid_roles:
                index = valid_roles.index(role_id)

                del valid_roles[index]

                data["valid-roles"] = valid_roles

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="ریمو کردن رول", description="شما این رول را حظف کردید!".format(role.name), color=0x00a8ff)

                await ctx.send(embed=em)
            
            else:
                
                em = discord.Embed(title="اکسس نداشتن", description="این رول به تیکت اکسس ندارد!", color=0x00a8ff)
                await ctx.send(embed=em)

        except:
            em = discord.Embed(title="اشتباه", description="این رول اشتباه است!")
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="نداشتن پرمیشن", description="ببخشید شما پرمیشن ندارید!", color=0x00a8ff)
        await ctx.send(embed=em)

@bot.command()
async def addpingedrole(ctx, role_id=None):

    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if valid_user or ctx.author.guild_permissions.administrator:

        role_id = int(role_id)

        if role_id not in data["pinged-roles"]:

            try:
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                data["pinged-roles"].append(role_id)

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="اد شد", description="شما با موفقیت رول  `{}` را به لیست اضافه کردید!".format(role.name), color=0x00a8ff)

                await ctx.send(embed=em)

            except:
                em = discord.Embed(title="اشتباه", description="این رول اشتباه است!")
                await ctx.send(embed=em)
            
        else:
            em = discord.Embed(title="دریافت پینگ", description="این نقش از قبل هنگام ایجاد بلیط ها پینگ دریافت می کند.", color=0x00a8ff)
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="نداشتن پرمیشن", description="ببخشید شما پرمیشن ندارید!", color=0x00a8ff)
        await ctx.send(embed=em)

@bot.command()
async def delpingedrole(ctx, role_id=None):

    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if valid_user or ctx.author.guild_permissions.administrator:

        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            pinged_roles = data["pinged-roles"]

            if role_id in pinged_roles:
                index = pinged_roles.index(role_id)

                del pinged_roles[index]

                data["pinged-roles"] = pinged_roles

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="حظف شد!", description="شما با موفقیت  `{}` را از لیست حظف کردید".format(role.name), color=0x00a8ff)
                await ctx.send(embed=em)
            
            else:
                em = discord.Embed(title="دریافت پینگ", description="این نقش از قبل هنگام ایجاد بلیط ها پینگ دریافت می کند", color=0x00a8ff)
                await ctx.send(embed=em)

        except:
            em = discord.Embed(title="رول اشتباه است!", description="شما رول را اشتباه وارد کردید!")
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="نداشتن پرمیشن", description="ببخشید شما پرمیشن ندارید!", color=0x00a8ff)
        await ctx.send(embed=em)


@bot.command()
@has_permissions(administrator=True)
async def addadminrole(ctx, role_id=None):

    try:
        role_id = int(role_id)
        role = ctx.guild.get_role(role_id)

        with open("data.json") as f:
            data = json.load(f)

        data["verified-roles"].append(role_id)

        with open('data.json', 'w') as f:
            json.dump(data, f)
        
        em = discord.Embed(title="اضافه شد", description="شما این رول را اضافه کردید!".format(role.name), color=0x00a8ff)
        await ctx.send(embed=em)

    except:
        em = discord.Embed(title="رول اشتباه است", description="شما رول اشتباه را اضافه کردید!")
        await ctx.send(embed=em)

@bot.command()
@has_permissions(administrator=True)
async def deladminrole(ctx, role_id=None):
    try:
        role_id = int(role_id)
        role = ctx.guild.get_role(role_id)

        with open("data.json") as f:
            data = json.load(f)

        admin_roles = data["verified-roles"]

        if role_id in admin_roles:
            index = admin_roles.index(role_id)

            del admin_roles[index]

            data["verified-roles"] = admin_roles

            with open('data.json', 'w') as f:
                json.dump(data, f)
            
            em = discord.Embed(title="حظف شد", description="شما این رول را حظف کردید!".format(role.name), color=0x00a8ff)

            await ctx.send(embed=em)
        
        else:
            em = discord.Embed(title="دریافت پینگ", description="این نقش از قبل هنگام ایجاد بلیط ها پینگ دریافت می کند", color=0x00a8ff)
            await ctx.send(embed=em)

    except:
        em = discord.Embed(title="رول را اشتباه وارد کردید", description="شما رول اشباهی را وارد کردید!")
        await ctx.send(embed=em)

bot.run("token")