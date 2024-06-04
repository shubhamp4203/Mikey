import discord
from discord.ext import commands
import re
from colorama import Fore
from discord.ui import Button, View
import sys
import os
import datetime
import typing
import json
import asyncio

        
class Myview(discord.ui.View):
    def __init__(self, ctx, timeout=30):
        super().__init__()
        self.ctx = ctx
        self.timeout = timeout

    async def interaction_check(self, interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You  cannot use that!!", ephemeral=True)
            return False
        else:
            return True

    async def on_timeout(self):
        self.clear_items()
        return

chardata = {}
with open('char_data.json', 'r') as f:
    cdict = json.load(f)

class Miscellaneous(commands.Cog):
    """
    Miscellaneous commands to make you feel good
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.date_dat = {"m" : [-10,-4,-6,-8,-4],
            "g" : [100,-4,-6,-8,-4],
            "f" : [0,-4,-6,92,-4],
            "n" : [0,-4,34,32,-4],
            "c" : [0,-4,54,-8,-4],
            "j" : [0,-4,54,-8,-4],
            "s" : [0,36,14,-8,-4],
            "t" : [0,56,-6,-8,-4],
            "i" : [0,56,-6,-8,-4],
            "fair" : [0,16,14,32,-4],
            "theatre" : [0,-4,-6,52,-4],
            "b" : [0,-14,-21,92,-4],
            "a" : [0,-4,-6,-18,-4],
            "shop" : [0,-4,-6,-8,-4],
            "r" : [0,-4,-6,-8,-4],
            "home" : [0,0,0,0,0]
        }
        self.date_objs = ["⛽ Gas", "🍔 Food", "🍹 Drink", "😌 Entertainment", "⌛ Time"]
        
    def chk_code(self, code):
        if code[0] in ["♡","★","☆","◈","#","✧"]:
            return False
        else:
            return True
    
    def date_f(self, in_str):
        initd = [100, 50, 50, 75, 100]
        in_str = in_str.lower()
        sep = " "
        if "," in in_str:
            sep = ","
        for obj in [i.strip() for i in in_str.split(sep)]:
            for obj_dat in self.date_dat.keys():
                if obj == obj_dat:
                    if obj == "home":
                        return f"""You will reach home with \n\n{self.date_objs[0]+" - "+str(initd[0])}\n{self.date_objs[1]+" - "+str(initd[1])}\n{self.date_objs[2]+" - "+str(initd[2])}\n{self.date_objs[3]+" - "+str(initd[3])}\n\n**BASED ON THE ABOVE VALUES YOU WILL GET APPROXIMATELY {round(((initd[1]+initd[2]+initd[3])/6)*(1-initd[4]/100))} AP**"""
                    for a_s,ind in zip(self.date_dat[obj_dat],range(5)):
                        initd[ind] += a_s
                        if initd[ind] > 100:
                            initd[ind] = 100
                        if initd[ind] < 1:
                            if ind == 4:
                                return f"""Congratulations your date will be successful\n\n{self.date_objs[0]+" - "+str(initd[0])}\n{self.date_objs[1]+" - "+str(initd[1])}\n{self.date_objs[2]+" - "+str(initd[2])}\n{self.date_objs[3]+" - "+str(initd[3])}\n\n**BASED ON THE ABOVE VALUES YOU WILL GET APPROXIMATELY {round((initd[1]+initd[2]+initd[3])/6)} AP**"""
                            return "Out of "+self.date_objs[ind]
                if obj not in self.date_dat.keys():
                    return f"❌ Invalid input `{obj}`"
        ret_str = ""
        for a,b in zip(self.date_objs, initd):
            ret_str += a+" : "+str(b)+"\n"
        return ret_str

    
    def chk_bits(self, bits):
        if bits[0] in ["·", "◾"]:
            return False
        else:
            return True


    @commands.command(name="wl-top")
    async def lbtop(self, ctx, arg=None):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        button1 = Button(label="<<", style=discord.ButtonStyle.green, custom_id="firstpage")
        button2 = Button(label="<", style=discord.ButtonStyle.green, custom_id="left")
        button3 = Button(label=">", style=discord.ButtonStyle.green, custom_id="right")
        button4 = Button(label=">>", style=discord.ButtonStyle.green, custom_id="lastpage")
        view = Myview(ctx, timeout=200)
        view.add_item(button1)
        view.add_item(button2)
        view.add_item(button3)
        view.add_item(button4)

        async def b1_callback(interaction):
            nonlocal cur_pagel
            cur_pagel = 1
            lembed = discord.Embed(title="Wishlist Leaderboard", description=f"\n{sorteddict[str(cur_pagel)]}Page: {1}/{pagesl}", color=0x00FFB7)
            if cur_pagel > 2 and cur_pagel < pagesl - 1:
                button4.disabled = False
                button3.disabled = False
                button2.disabled = False
                button1.disabled = False
            elif cur_pagel == 1:
                button2.disabled = True
                button1.disabled = True
                button3.disabled = False
                button4.disabled = False
            elif cur_pagel > 1 and cur_pagel < pagesl - 1:
                button2.disabled = False
                button3.disabled = False
                button4.disabled = False
                button1.disabled = True
            elif cur_pagel == pagesl:
                button4.disabled = True
                button3.disabled = True
                button1.disabled = False
                button2.disabled = False
            elif cur_pagel < pagesl and cur_pagel > 2:
                button3.disabled = False
                button4.disabled = True
                button1.disabled = False
                button2.disabled = False
            await interaction.response.edit_message(embed=lembed, view=view)
            return

        async def b2_callback(interaction):
            nonlocal cur_pagel
            cur_pagel -= 1
            lembed = discord.Embed(title="Wishlist Leaderboard", description=f"\n{sorteddict[str(cur_pagel)]}Page: {cur_pagel}/{pagesl}", color=0x00FFB7)
            if cur_pagel > 2 and cur_pagel < pagesl - 1:
                button4.disabled = False
                button3.disabled = False
                button2.disabled = False
                button1.disabled = False
            elif cur_pagel == 1:
                button2.disabled = True
                button1.disabled = True
                button3.disabled = False
                button4.disabled = False
            elif cur_pagel > 1 and cur_pagel < pagesl - 1:
                button2.disabled = False
                button3.disabled = False
                button4.disabled = False
                button1.disabled = True
            elif cur_pagel == pagesl:
                button4.disabled = True
                button3.disabled = True
                button1.disabled = False
                button2.disabled = False
            elif cur_pagel < pagesl and cur_pagel > 2:
                button3.disabled = False
                button4.disabled = True
                button1.disabled = False
                button2.disabled = False
            await interaction.response.edit_message(embed=lembed, view=view)
            return

        async def b3_callback(interaction):
            nonlocal cur_pagel
            cur_pagel += 1
            lembed = discord.Embed(title="Wishlist Leaderboard", description=f"\n{sorteddict[str(cur_pagel)]}Page: {cur_pagel}/{pagesl}", color=0x00FFB7)
            if cur_pagel > 2 and cur_pagel < pagesl - 1:
                button4.disabled = False
                button3.disabled = False
                button2.disabled = False
                button1.disabled = False
            elif cur_pagel == 1:
                button2.disabled = True
                button1.disabled = True
                button3.disabled = False
                button4.disabled = False
            elif cur_pagel > 1 and cur_pagel < pagesl - 1:
                button2.disabled = False
                button3.disabled = False
                button4.disabled = False
                button1.disabled = True
            elif cur_pagel == pagesl:
                button4.disabled = True
                button3.disabled = True
                button1.disabled = False
                button2.disabled = False
            elif cur_pagel < pagesl and cur_pagel > 2:
                button3.disabled = False
                button4.disabled = True
                button1.disabled = False
                button2.disabled = False
            await interaction.response.edit_message(embed=lembed, view=view)
            return

        async def b4_callback(interaction):
            nonlocal cur_pagel
            cur_pagel = pagesl
            lembed = discord.Embed(title="Wishlist Leaderboard",description=f"\n{sorteddict[str(cur_pagel)]}Page: {cur_pagel}/{pagesl}",color=0x00FFB7)
            if cur_pagel > 2 and cur_pagel < pagesl - 1:
                button4.disabled = False
                button3.disabled = False
                button2.disabled = False
                button1.disabled = False
            elif cur_pagel == 1:
                button2.disabled = True
                button1.disabled = True
                button3.disabled = False
                button4.disabled = False
            elif cur_pagel > 1 and cur_pagel < pagesl - 1:
                button2.disabled = False
                button3.disabled = False
                button4.disabled = False
                button1.disabled = True
            elif cur_pagel == pagesl:
                button4.disabled = True
                button3.disabled = True
                button1.disabled = False
                button2.disabled = False
            elif cur_pagel < pagesl and cur_pagel > 2:
                button3.disabled = False
                button4.disabled = True
                button1.disabled = False
                button2.disabled = False
            await interaction.response.edit_message(embed=lembed, view=view)
            return

        with open("lb_data.json", "r") as f:
            sorteddict = json.load(f)
        pagesl = len(sorteddict.keys())
        cur_pagel = 1
        button1.callback = b1_callback
        button2.callback = b2_callback
        button3.callback = b3_callback
        button4.callback = b4_callback


        if arg != None:
            if arg.isdigit() == True and int(arg) <= pagesl:
                lembed = discord.Embed(title="Wishlist Leaderboaard",description=f"\n{sorteddict[arg]}Page: {arg}/{pagesl}",color=0x00FFB7)
                await ctx.channel.send(embed=lembed)
                return

        button1.disabled = True
        button2.disabled = True
        lembed = discord.Embed(title="Wishlist Leaderboaard", description=f"\n{sorteddict[str(cur_pagel)]}Page: {cur_pagel}/{pagesl}", color=0x00FFB7)
        await ctx.channel.send(embed=lembed, view=view)

    '''@commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id != 646937666251915264:
            return
        if not msg.embeds:
            return
        if "Character Lookup" not in msg.embeds[0].title:
            return
        desp = msg.embeds[0].description
        verify = desp.split("·")[2].split("\n")[1]
        if verify == "Koibito ":
            wl = desp.split("·")[4].split("\n")[0].split("**")[1].replace(",", "")
            wl = int(wl)
            series_name = desp.split("·")[2].split("\n")[0].split("**")[1].replace(r"\u00e9", "é")
            char_name = desp.split("·")[1].split("\n")[0].split("**")[1]
        else:
            wl = desp.split("·")[3].split("\n")[0].split("**")[1].replace(",", "")
            wl = int(wl)
            series_name = desp.split("·")[2].split("\n")[0].split("**")[1].replace(r"\u00e9", "é").replace(
                r"\u00eb", "ë")
            char_name = desp.split("·")[1].split("\n")[0].split("**")[1]

        if not wl > 100:
            return
        chardata[char_name] = {series_name: wl}
        lot = []
        for k, v in chardata.items():
            k_, v_ = next(iter(v.items()))
            lot.append((v_, k_, k))
        sorted_dict = {a: {b: c} for c, b, a in sorted(lot, reverse=True)}
        with open('char_data.json', 'w') as file:
            json.dump(sorted_dict, file, indent=4)'''

    '''@commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id != 646937666251915264:
            return
        if "took the" not in msg.content:
            return
        char_name = msg.content.split("**")[1]
        if char_name not in cdict.keys():
            return
        send_channel = self.bot.get_channel(870275991883358278)
        await send_channel.send(msg.content)'''

    @commands.command(name="affordable-frame", aliases=["af"])
    async def posframe(self, ctx):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        user_data = []
        frame_data = {"brass": [' Copper Bit ', ' Zinc Bit '], "fortress": [' Stone Bit ', ' Wood Bit '],
                      "beachside": [' Flower Bit ', ' Quartz Bit '], "volcanic": [' Copper Bit ', ' Magma Bit '],
                      "cherry blossom": [' Flower Bit ', ' Wood Bit '], "spirit flame": [' Bone Bit ', ' Wood Bit '],
                      "night crow": [' Bone Bit ', ' Zinc Bit '], "crystal mines": [' Quartz Bit ', ' Stone Bit '],
                      "submarine": [' Iron Bit ', ' Uranium Bit '], "pirate voyage": [' Iron Bit ', ' Wood Bit '],
                      "kominka": [' Essence Bit ', ' Wood Bit '], "magus": [' Essence Bit ', ' Zinc Bit '],
                      "magitek": [' Magma Bit ', ' Uranium Bit '], "snowlands": [' Ice Bit ', ' Wood Bit '],
                      "ice cream sundae": [' Ice Bit ', ' Sugar Bit '], "dragon hunt": [' Bone Bit ', ' Wool Bit '],
                      "patchwork": [' Essence Bit ', ' Wool Bit '], "venice carnival": [' Flower Bit ', ' Zinc Bit '],
                      "robotic": [' Essence Bit ', ' Uranium Bit '], "frills": [' Quartz Bit ', ' Wool Bit '],
                      "fuselage": [' Iron Bit ', ' Zinc Bit '], "rozen": [' Flower Bit ', ' Stone Bit '],
                      "smithy forge": [' Magma Bit ', ' Stone Bit '], "Watermelon juice": [' Leaf Bit ', ' Sugar Bit '],
                      "Whirlpool": [' Ice Bit ', ' Salt Bit '], "Barbecue": [' Salt Bit ', ' Zinc Bit '], "Edo Furin": [' Copper Bit ', ' Quartz Bit '],
                      "Autumn View": [' Leaf Bit ', ' Stone Bit '], "Faerie Forest": [' Flower Bit ', ' Leaf Bit '], "Tree Frog": [' Bone Bit ', ' Leaf Bit '],
                      "Archery": [' Copper Bit ', ' Wood Bit '], "Wild West": [' Quartz Bit ', ' Wood Bit '], "Spaceship": [' Uranium Bit ', ' Zinc Bit '],
                      "Bubble Bath": [' Ice Bit ', ' Wool Bit '], "Abandoned Church": [' Leaf Bit ', ' Quartz Bit '], "Tribal Chief": [' Copper Bit ', ' Stone Bit '],
                      "Chocolate Orange": [' Essence Bit ', ' Sugar Bit '], "Bamboo Stalks": [' Leaf Bit ', ' Wood Bit '], "Scimitar Fight": [' Bone Bit ', ' Iron Bit '],
                      "Carnations": [' Flower Bit ', ' Wool Bit '], "Beauty": [' Clay Bit ', ' Flower Bit '], "Carved Stone": [' Clay Bit ', ' Stone Bit '],
                      "Water Element": [' Ice Bit ', ' Quartz Bit '], "Long Hair": [' Essence Bit ', ' Salt Bit '], "Musical Notes": [' Essence Bit ', ' Iron Bit '],
                      "Baroque": [' Clay Bit ', ' Copper Bit '], "Manticore": [' Bone Bit ', ' Magma Bit '], "Winners Podium": [' Iron Bit ', ' Stone Bit '],
                      "Morning Dew": [' Flower Bit ', ' Ice Bit '], "Bubble Tea": [' Ice Bit ', ' Leaf Bit '], "Toy Mecha": [' Ice Bit ', ' Uranium Bit '],
                      "Shiba Inu": [' Bone Bit ', ' Essence Bit '], "Nordic": [' Salt Bit ', ' Stone Bit '], "Tipsy": [' Salt Bit ', ' Sugar Bit '], "Magical Girl": [' Quartz Bit ', ' Sugar Bit '],
                      "Honeycomb": [' Sugar Bit ', ' Wax Bit '], "Nurses Office": [' Bone Bit ', ' Sugar Bit '], "Tetromino": [' Essence Bit ', ' Wax Bit '], "Flying Dragon": [' Bone Bit ', ' Oil Bit '],
                      "Gaming Chair": [' Oil Bit ', ' Wool Bit '], "Tanglung": [' Flower Bit ', ' Oil Bit '], "Pastel Geometry": [' Wax Bit ', ' Uranium Bit '], "Lightroom Storm": [' Ice Bit ', ' Stone Bit '],
                      "Chopsticks": [' Salt Bit ', ' Wood Bit '], "Haunted Stone": [' Essence Bit ', ' Stone Bit '], "Kawaii Bento": [' Salt Bit ', ' Wool Bit '], "Pockey Pet": [' Bone Bit ', ' Clay Bit ']
                      }
        ab_msg = await ctx.channel.send("Please do kbi.")

        def check(m):
            return m.author.id == 646937666251915264 and m.channel == ctx.channel and m.embeds and m.embeds[0].description.split("\n")[0].split(" ")[3].replace("<@", "").replace(">", "") == str(ctx.author.id)

        try:
            message = await self.bot.wait_for('message', timeout=30, check=check)
        except asyncio.TimeoutError:
            await ab_msg.edit("You didn't kbi in time.")
            return
        desp = message.embeds[0].description.split("\n")
        if len(desp) == 1:
            await ctx.channel.send("Sorry you cannot buy any frame :(")
            return
        desp.pop(0)
        desp.pop(0)

        def me_check(msg_b, e_msg):
            return msg_b.id == message.id
        for i in desp:
            bitname = i.split("·")[1].replace("`", "").title()
            amt_list = []
            amtbit = ""
            for j in i:
                if j.isdigit():
                    amt_list.append(j)
            amtbit = int(amtbit.join(amt_list))
            if amtbit >= 2500:
                user_data.append(bitname)
        footer = message.embeds[0].footer.text
        total_bits = int(footer[len(footer)-2:])
        if not total_bits <= 10:
            await ab_msg.edit("**Please show second page.**")
            while True:
                try:
                    msg_b, e_msg = await self.bot.wait_for('message_edit', timeout=30, check=me_check)
                except:
                    return
                despe = e_msg.embeds[0].description.split("\n")
                despe.pop(0)
                despe.pop(0)
                for i in despe:
                    bitname = i.split("·")[1].replace("`", "").title()
                    amt_list = []
                    amtbit = ""
                    for j in i:
                        if j.isdigit():
                            amt_list.append(j)
                    amtbit = int(amtbit.join(amt_list))
                    if amtbit >= 2500:
                        user_data.append(bitname)
                a = list(set(user_data))
                textlist = []
                set2 = set(a)
                for j in frame_data.keys():
                    set1 = set(frame_data[j])
                    if set1.issubset(set2) != True:
                        continue
                    else:
                        textlist.append(j.title())

                if len(textlist) == 0:
                    await ctx.channel.send("Sorry you cannot buy any frame :(")
                    return
                text = " - ".join(textlist)
                send_enmbed = discord.Embed(title="Affordable Frames", description=f"```\n{text}```", color=0x00FFFF)
                but = Button(label="✔", style=discord.ButtonStyle.green)
                view = Myview(ctx)
                view.add_item(but)
                async def but_callback(interaction):
                    await interaction.response.send_message(embed= send_enmbed, ephemeral=True)
                    view.stop()
                    return
                but.callback = but_callback
                await ctx.channel.send("Click the button to get the list of buyable frames.", view=view)
                await view.wait()
                return
        textlist = []
        set2 = set(user_data)
        for j in frame_data.keys():
            set1 = set(frame_data[j])
            if set1.issubset(set2) != True:
                continue
            else:
                textlist.append(j.title())
        if len(textlist) == 0:
            await ctx.channel.send("Sorry you cannot buy any frame :(")
            return
        text = " - ".join(textlist)
        but = Button(label="✔", style=discord.ButtonStyle.green)
        view = Myview(ctx)
        view.add_item(but)

        async def but_callback(interaction):
            await interaction.response.send_message(embed=send_enmbed, ephemeral=True)
            view.stop()
            return

        but.callback = but_callback
        send_enmbed = discord.Embed(title="Affordable Frames", description=f"```\n{text}```", color=0x00FFFF)
        await ctx.channel.send("Click the button to get the list of buyable frames.", view=view)
        await view.wait()
        return

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != 866904114952142849:
            return
        if message.author.id != 646937666251915264:
            return
        if not message.embeds:
            return
        if message.embeds[0].title not in ["View Clan","Clan Contribution"]:
            return
        def check_rl(reaction,user):
            return str(reaction.emoji) == "⚡" and reaction.message.id == message.id and self.bot.user != user
        await message.add_reaction("⚡")
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout = 20 ,check = check_rl)
        except:
            return
        rep = message.embeds[0].description
        for field in message.embeds[0].fields:
            rep += "\n"+field.name+field.value
        await message.channel.send(rep.replace("@",""))
    
    
    @commands.command(name="bits")
    async def countbits(self, ctx):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if not(ctx.message.reference):
            return
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if message.author.id == 646937666251915264 and message.embeds[0].title == "Bits":
            name_str = list(filter(self.chk_bits, message.embeds[0].description.split("**")[2::2]))
            bit_str = list(filter(self.chk_bits, message.embeds[0].description.split("**")[1::2]))
            str_list = [s.replace(",", "") for s in bit_str]
            int_list = [int(x) for x in str_list]
            pattern = "\`(.*?)\`"
            wname = [re.search(pattern, s).group(1) for s in name_str]
            final_list = [f"{str_list[a]} {wname[a]}" for a in range(len(bit_str))]
            final_msg = "`"+ ",".join(final_list) + "`"+"="+f"**{sum(int_list)}** Bits"
            sent_msg = await ctx.channel.send(final_msg)
            def me_check(msg_b,e_msg):
                return msg_b.id == message.id
            while True:
                try:
                    msg_b,e_msg = await self.bot.wait_for('message_edit', timeout = 30 ,check = me_check)
                except:
                    return
                newname_str =  list(filter(self.chk_bits, e_msg.embeds[0].description.split("**")[2::2]))
                newbit_str = list(filter(self.chk_bits, e_msg.embeds[0].description.split("**")[1::2]))
                if newbit_str == bit_str:
                    return
                newstr_list = [s.replace(",", "") for s in newbit_str]
                newint_list = [int(x) for x in newstr_list]
                pattern = "\`(.*?)\`"
                newwname = [re.search(pattern, s).group(1) for s in newname_str]
                new_list = [f"{newstr_list[a]} {newwname[a]}" for a in  range(len(newstr_list))]
                nfinal_list = [s for s in new_list if s not in final_list]
                newfinal_list = final_list + nfinal_list 
                nint_list = [int(s.split(" ")[0]) for s in newfinal_list]
                final_msg = "`"+",".join(newfinal_list) + "`"+"="+f"**{sum(nint_list)}** Bits"
                await sent_msg.edit(content=final_msg)
    
        
    @commands.command(name = "codes")
    async def codes_ex(self, ctx):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if not(ctx.message.reference):
            return
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if message.author.id == 646937666251915264 and message.embeds[0].title == "Card Collection":
            ret_str = ", ".join(list(filter(self.chk_code,
            message.embeds[0].description.split("`")[1::2])))
            snt_msg = await ctx.channel.send(f"`{ret_str}`")
            def me_check(msg_b,e_msg):
                return msg_b.id == message.id
            while True:
                try:
                    msg_b,e_msg = await self.bot.wait_for('message_edit', timeout = 15 ,check = me_check)
                except:
                    return
                ret_str += ", " + ", ".join(list(filter(self.chk_code,
                e_msg.embeds[0].description.split("`")[1::2])))
                await snt_msg.edit(f"`{ret_str}`")


    @commands.command(name = 'announce')
    @commands.has_permissions(administrator=True)
    async def sndembed(self, ctx, *, w_msg):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        text = w_msg.split("\n",1)[1]
        e_url = ""
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        for url in urls:
            if url.endswith(".png") or url.endswith(".jpg"):
                e_url = url
                break
        try:
            embed = discord.Embed(colour = self.bot.ecolor, title = w_msg.split("\n")[0], description = w_msg.split("\n",1)[1].replace(e_url, ""))
            if e_url:
                embed.set_image(url = e_url)
            await ctx.channel.send(embed=embed)
        except:
            return
   
    @commands.command(name= "say")
    async def say(self, ctx, *, msg):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if ctx.author.id not in [569168901204606996, 840224507036696616]:
            return
        await ctx.message.delete()
        await ctx.channel.send(msg)

    @commands.command(name = "date")
    async def date_calc(self, ctx,*,inp_str = None):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if inp_str == None:
            return
        embed = discord.Embed(colour = self.bot.ecolor, title = "Date Calculator", description = self.date_f(inp_str))
        await ctx.channel.send(embed = embed)
    
    @commands.command(name = 'set-wishwatch', pass_context=True, aliases = ["set-ww"])
    async def setwwrole(self, ctx,role_id : discord.Role = None):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if not(ctx.message.author.guild_permissions.administrator):
            await ctx.channel.send(f"<@{str(ctx.author.id)}>, you do not have proper permissions to use this command.")
            return
        try:
            role_id = role_id.id
        except:
            role_id = None
        sd_v = self.bot.dfread("servers_dat")
        unset_cond = False
        if "wlrole" in sd_v[str(ctx.guild.id)]:
            if sd_v[str(ctx.guild.id)]["wlrole"] > 999:
                unset_cond = True
        if role_id == None and not unset_cond:
            await ctx.channel.send(f"Please specify a proper role. Use `m.set-wishwatch <role/id>`")
            return
        if unset_cond:
            temp_doc = {"wlrole" : role_id}
            self.bot.serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$unset" : temp_doc})
            sd_v[str(ctx.guild.id)].pop("wlrole")
            self.bot.dfwrite("servers_dat",sd_v)
            await ctx.channel.send(f'<@{ctx.author.id}>, you have unset wishwatch ping.')
            return
        temp_doc = {"wlrole" : role_id}
        self.bot.serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$set" : temp_doc})
        sd_v[str(ctx.guild.id)]["wlrole"] = role_id
        self.bot.dfwrite("servers_dat",sd_v)
        embed = discord.Embed(colour = 0x00FFFF, description = f'Wishwatch role set to <@&{role_id}> role.')
        await ctx.channel.send(embed = embed)

    
    @commands.command(name = "wishwatch", aliases = ["ww"])
    async def give_role(self, ctx):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        sd_v = self.bot.dfread("servers_dat")
        if "wlrole" not in sd_v[str(ctx.guild.id)]:
            return
        role = discord.utils.get(ctx.guild.roles, id = sd_v[str(ctx.guild.id)]["wlrole"])
        try:
            if role in ctx.author.roles:
                await ctx.author.remove_roles(role)
                await ctx.channel.send("Role removed successfully")
            else:
                await ctx.author.add_roles(role)
                await ctx.channel.send("Role given successfully")
        except:
            await ctx.channel.send("Bot is missing manage role permission.")
            
    @commands.command(name = "avatar", aliases = ['av'])
    async def avatar(self, ctx,avmem : discord.Member=None):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        elif avmem == None:
            avmem = ctx.author
        userav = avmem.display_avatar.url
        embed = discord.Embed(colour = self.bot.ecolor, description = avmem.mention)
        embed.set_image(url = userav)
        embed.set_footer(text="Requested by user : "+str(ctx.author))
        await ctx.channel.send(embed=embed)
    
    
    @commands.command(name = 'prefix')
    @commands.has_permissions(manage_guild=True)
    async def changeprefix(self, ctx, prefix : str = None):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        
        sd_v = self.bot.dfread("servers_dat")
        
        if self.bot.server_prefix.get(ctx.guild.id):
            p_prefix = self.bot.server_prefix[ctx.guild.id]
        else:
            p_prefix = "m."
            
        if not prefix:
            await ctx.channel.send(f"Bot prefix in this server is : `{p_prefix}`")
            return
        
        if len(prefix)>8 or " " in prefix:
            await ctx.channel.send("Invalid prefix.")
            return
        
        temp_doc = {"prefix" : prefix}
        self.bot.serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$set" : temp_doc})
        sd_v[str(ctx.guild.id)]["prefix"] = prefix
        self.bot.dfwrite("servers_dat",sd_v)
        embed = discord.Embed(colour = self.bot.ecolor, description = f'Bot prefix in this server changed to  :  **{prefix}**')
        self.bot.server_prefix[ctx.guild.id] = prefix
        await ctx.channel.send(embed = embed)
    
    
    @commands.command(name = "status", description = "Owner Only")
    @commands.is_owner()
    async def sbstatus(self, ctx,*,status_m: str):
        self.bot.stat = status_m
        await ctx.reply(f"Status Changed Successfully: `{self.bot.stat}`")
    
    @commands.command(aliases=["rerun", "reboot"])
    @commands.is_owner()
    async def restart(self, ctx):
        restartem = discord.Embed(color=discord.Color.dark_orange(), title=f"RESTARTING...", description= f"Restart command was executed by {ctx.author.mention}\nPlease check <#{870275991883358278}> for the logs!")
        restartem.set_footer(text=f"{self.bot.user.name}", icon_url=ctx.author.display_avatar.url)

        await ctx.reply(embed=restartem)

        print(Fore.YELLOW + f'Restart command executed by {ctx.author}! Restarting...')

        os.execv(sys.executable, [sys.executable] + sys.argv)
        
        
    @commands.command(aliases=["blacklistuser", "botban"])
    @commands.is_owner()
    async def blacklist(self, ctx, user, *, reason):
        try:
            user = await discord.ext.commands.UserConverter().convert(ctx, user)
        except:
            return await ctx.reply("Please mention the user in a correct way!")
        if not reason:
            return await ctx.reply('Please mention the reason!')
        usr = await self.bot.evalsql(database='./Database/blacklist.db', sql='SELECT * FROM users WHERE user_id=?', vals=(user.id,), fetch='one')
        if not usr:
            await self.bot.evalsql(database='./Database/blacklist.db', sql='INSERT OR IGNORE INTO users VALUES(?, ?, ?)', vals=(user.id, str(datetime.datetime.now()), reason))
            em = discord.Embed(title=f"SUCCESSFULLY BOT BANNED USER", color=0xff0000)
            em.description = f"`{user.name}` `({user.id})`has been blacklisted!"
            em.add_field(name="Reason", value=reason)
            em.set_footer(icon_url= self.bot.user.display_avatar.url)
            em.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(title=f"THE USER IS ALREADY BANNED", description=f"The user is already bot-banned with reason:\n> {usr['reason']}", color=0xff0000)
            em.set_footer(icon_url= ctx.guild.icon.url)
            em.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(embed=em)
            
            
    @commands.command(aliases=["unbanbot", "botunban"])
    @commands.is_owner()
    async def unblacklist(self, ctx, *, user):
        try:
            user = await discord.ext.commands.UserConverter().convert(ctx, user)
        except:
            return await ctx.reply("Please mention the user in a correct way!")
        usr = await self.bot.evalsql(database='./Database/blacklist.db', sql='SELECT * FROM users WHERE user_id=?', vals=(user.id,), fetch='one')
        if usr != None:
            await self.bot.evalsql(database='./Database/blacklist.db', sql='DELETE FROM users WHERE user_id=?', vals=(user.id,))
            em = discord.Embed(title=f"SUCCESSFULLY UNBANNED USER", color=0xff0000)
            em.description = f"`{user.name}` `({user.id})`has been unbanned from using the bot."
            em.set_footer(icon_url= self.bot.user.display_avatar.url)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(title=f"THE USER WAS NEVER BANNED", description=f"The user was never banned from using the bot!", color=0xff0000)
            em.set_footer(icon_url= ctx.guild.icon.url)
            await ctx.send(embed=em)
        
    @commands.command(aliases=["showbanned", "showbotbanned"])
    @commands.is_owner()
    async def showblacklist(self, ctx):
        users = await self.bot.evalsql(database='./Database/blacklist.db', sql='SELECT * FROM users', fetch='all')
        if len(users) == 0:
            return await ctx.reply("The list is empty!")
        li = []
        for user in users:
            ud = user['user_id']
            try:
                un = await self.bot.fetch_user(ud)
                li.append(f"{un} ({ud})")
            except:
                li.append(f"User ID: {ud}")
        sr = "\n".join(x for x in li)
        await ctx.reply(f"```{sr}```")

    @commands.command(name="sil")
    async def serverlist(self, ctx):
        if ctx.channel.id != 870275991883358278:
            return
        for guild in self.bot.guilds:
            if guild.member_count > 100000:
                await ctx.channel.send(f"{guild} - {guild.id}") 

    @commands.command(name="leave", aliases=['ls'])
    async def leaveserver(self, ctx, serverid):
        if ctx.author.bot:
            return
        if ctx.author.id not in [840224507036696616, 843400308008812545, 569168901204606996]:
            await ctx.reply("You cannot use that command!")
            return
        if serverid.isdigit() == False:
            await ctx.reply("Enter a valid server id.")
            return
        serverid = int(serverid)
        guild = self.bot.get_guild(serverid)
        if guild == None:
            await ctx.reply("Sorry I am not in that guild")
            return
        await guild.leave()
        await ctx.reply(f"Successfully left the {guild} server")

    @commands.command(name="serverinfo", aliases=['si'])
    async def serverinfo(self, ctx, server_id):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if ctx.author.id not in [528038349802438666, 761923749179162675, 847124538721435659, 569168901204606996, 840224507036696616,843400308008812545]:
            await ctx.reply("You cannot use that command!")
            return
        if server_id.isdigit() == False:
            await ctx.reply("Enter a valid server id.")
            return

        server_id = int(server_id)
        guild = self.bot.get_guild(server_id)
        if guild == None:
            await ctx.reply("Sorry I am not in that guild")
            return
        server_owner = await self.bot.fetch_user(guild.owner_id)
        infoembed = discord.Embed(title=f"{guild}'s Server Info", color=0x00FFB7)
        infoembed.set_thumbnail(url=guild.icon.url if guild.icon != None else "")
        infoembed.add_field(name="**Server Owner**", value=f"{server_owner}", inline=True)
        infoembed.add_field(name="**Owner Id**", value=f"{guild.owner_id}", inline=True)
        infoembed.add_field(name="**Server created on**", value=f"{guild.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
                            inline=True)
        infoembed.add_field(name="**Total Channels**", value=f"{len(guild.channels)}", inline=True)
        infoembed.add_field(name="**Total Members**", value=f"{guild.member_count}", inline=True)
        infoembed.add_field(name="**Shard Id**", value=f"{guild.shard_id}", inline=True)
        await ctx.reply(embed=infoembed)

    @commands.command(name="ms", aliases=[])
    #@commands.is_owner()
    async def mutualsrvinfo(self, ctx, user_id : int):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if ctx.author.id not in [528038349802438666, 761923749179162675, 847124538721435659, 569168901204606996, 840224507036696616, 843400308008812545]:
            await ctx.reply("You cannot use that command!")
            return
        dsp_str = "**Name | Id | Members**\n\n"
        c = 0
        for guild_obc in self.bot.guilds:
            guild = self.bot.get_guild(guild_obc.id)
            try:
                await guild.fetch_member(user_id)
            except Exception as e:
                #print(e)
                continue
            dsp_str += f"**`{guild.name}`** · `{guild.id}` · `{guild.member_count}`\n"
            if c>30:
                break
            c += 1
        infoembed = discord.Embed(title=f"Mutual Servers", description = dsp_str, color=0x00FFB7)
        await ctx.reply(embed=infoembed)
        
        
def setup(bot):
    bot.add_cog(Miscellaneous(bot))
