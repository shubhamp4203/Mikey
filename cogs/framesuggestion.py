import json

import discord
from discord.ext import commands
import asyncio
from discord.ui import Button, View
import asyncio

with open('framesuggestiondata.json', 'r') as f:
    cdict = json.load(f)
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

class FrameSuggestion(commands.Cog):
    """
    Suggest frames for the bot. Use frame-suggest command.
    """
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name = "frame-suggest", aliases = ["fs"], description= "m.fs <char_name> <ed1/ed2/ed3>")
    async def fsuggest(self, ctx, *, arg):
        uid = ctx.author.name
        argl = arg.split(" ")
        if ctx.channel.id in [887219466088374272, 875275103238242365]:
            await ctx.reply("You cannot use that command here!")
            return



        upage = argl[-1].lower()

        if upage == "list":
            clist = {0:""}
            pgno = 0
            cardno = 1
            indexno = 1
            for i in cdict.keys():
                clist[pgno] += f"{cardno}. {cdict[i]['cname'].title()}\n"
                cardno += 1
                indexno += 1
                if indexno == 21:
                    pgno += 1
                    clist[pgno] = ""
                    indexno = 1
            if clist[len(clist.keys())-1] == "":
                clist.pop(len(clist.keys())-1)
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
                lembed = discord.Embed(title="Character List",
                                       description=f"\n```py\n{clist[cur_pagel-1]}```Page: {1}/{pagesl}", color=0x00FFB7)
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
                lembed = discord.Embed(title="Character List",
                                       description=f"\n```py\n{clist[cur_pagel-1]}```Page: {cur_pagel}/{pagesl}",
                                       color=0x00FFB7)
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
                lembed = discord.Embed(title="Character List",
                                       description=f"\n```py\n{clist[cur_pagel-1]}```Page: {cur_pagel}/{pagesl}",
                                       color=0x00FFB7)
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
                lembed = discord.Embed(title="Character List",
                                       description=f"\n```py\n{clist[cur_pagel-1]}```Page: {cur_pagel}/{pagesl}",
                                       color=0x00FFB7)
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

            pagesl = len(clist.keys())
            cur_pagel = 1

            button1.callback = b1_callback
            button2.callback = b2_callback
            button3.callback = b3_callback
            button4.callback = b4_callback

            lembed = discord.Embed(title="Character List", description=f"\n```py\n{clist[cur_pagel-1]}```Page: {cur_pagel}/{pagesl}", color = 0x00FFB7)
            button1.disabled = True
            button2.disabled = True
            await ctx.channel.send(embed=lembed, view = view)
            return
        if upage in ["1","2","3","4","5","6","7","8"] and argl[0].lower() == "list":
            clist = {0: ""}
            pgno = 0
            cardno = 1
            indexno = 1
            for i in cdict.keys():
                clist[pgno] += f"{cardno}. {cdict[i]['cname'].title()}\n"
                cardno += 1
                indexno += 1
                if indexno == 21:
                    pgno += 1
                    clist[pgno] = ""
                    indexno = 1
            if clist[len(clist.keys())-1] == "":
                clist.pop(len(clist.keys())-1)
            print(clist)
            pagesl = len(clist.keys())
            lembed = discord.Embed(title="Character List",description=f"\n```py\n{clist[int(upage)-1]}```Page: {upage}/{pagesl}", color=0x00FFB7)
            await ctx.channel.send(embed=lembed)
            return
        if argl[0].lower() not in cdict:
            if len(argl) > 1:
                cstr = argl[0:len(argl)-1]
                argl[0] = f"{cstr[0]} {cstr[len(cstr)-1]}"
            if argl[0].lower() not in cdict:
                await ctx.channel.send("Sorry I could not suggest frames for that character or it is not added yet.")
                return
        if argl[-1].lower() == "all":
            cembed1 = discord.Embed(title="**Frame Suggestions**", description=f"**Character Name**: {cdict[argl[0].lower()]['cname'].title()} ({'ed1'.capitalize()})\n\n**Bit Frames**:\n```\n{cdict[argl[0].lower()]['ed1']['bframe'].title()}```\n**Gem Frames**:\n```\n{cdict[argl[0].lower()]['ed1']['gframe'].title()}```\n**Carousel Frames**:\n```\n{cdict[argl[0].lower()]['ed1']['cframe'].title()}```\n**Event Frames**:\n```\n{cdict[argl[0].lower()]['ed1']['eframe'].title()}```\nWe have collaborated with Keqing Bot\nFor frame testing use [Keqing Bot](https://top.gg/bot/772642704257187840), [Keqing Support](https://discord.gg/8pMnSqweut)", color=0x00FFB7)
            cembed1.set_thumbnail(url=f"{cdict[argl[0].lower()]['ed1']['url']}")
            cembed1.set_footer(text=f"Requested by {uid}")
            cembed2 = discord.Embed(title="**Frame Suggestions**", description=f"**Character Name**: {cdict[argl[0].lower()]['cname'].title()} ({'ed2'.capitalize()})\n\n**Bit Frames**:\n```\n{cdict[argl[0].lower()]['ed2']['bframe'].title()}```\n**Gem Frames**:\n```\n{cdict[argl[0].lower()]['ed2']['gframe'].title()}```\n**Carousel Frames**:\n```\n{cdict[argl[0].lower()]['ed2']['cframe'].title()}```\n**Event Frames**:\n```\n{cdict[argl[0].lower()]['ed2']['eframe'].title()}```\nWe have collaborated with Keqing Bot\nFor frame testing use [Keqing Bot](https://top.gg/bot/772642704257187840), [Keqing Support](https://discord.gg/8pMnSqweut)", color=0x00FFB7)
            cembed2.set_thumbnail(url=f"{cdict[argl[0].lower()]['ed2']['url']}")
            cembed2.set_footer(text=f"Requested by {uid}")
            cembed3 = discord.Embed(title="**Frame Suggestions**", description=f"**Character Name**: {cdict[argl[0].lower()]['cname'].title()} ({'ed3'.capitalize()})\n\n**Bit Frames**:\n```\n{cdict[argl[0].lower()]['ed3']['bframe'].title()}```\n**Gem Frames**:\n```\n{cdict[argl[0].lower()]['ed3']['gframe'].title()}```\n**Carousel Frames**:\n```\n{cdict[argl[0].lower()]['ed3']['cframe'].title()}```\n**Event Frames**:\n```\n{cdict[argl[0].lower()]['ed3']['eframe'].title()}```\nWe have collaborated with Keqing Bot\nFor frame testing use [Keqing Bot](https://top.gg/bot/772642704257187840), [Keqing Support](https://discord.gg/8pMnSqweut)", color=0x00FFB7)
            cembed3.set_thumbnail(url=f"{cdict[argl[0].lower()]['ed3']['url']}")
            cembed3.set_footer(text=f"Requested by {uid}")
            econtents = [cembed1, cembed2, cembed3]
            if len(cdict[argl[0].lower()].keys()) == 5  :
                cembed4 = discord.Embed(title="**Frame Suggestions**",
                                        description=f"**Character Name**: {cdict[argl[0].lower()]['cname'].title()} ({'ed4'.capitalize()})\n\n**Bit Frames**:\n```\n{cdict[argl[0].lower()]['ed4']['bframe'].title()}```\n**Gem Frames**:\n```\n{cdict[argl[0].lower()]['ed4']['gframe'].title()}```\n**Carousel Frames**:\n```\n{cdict[argl[0].lower()]['ed4']['cframe'].title()}```\n**Event Frames**:\n```\n{cdict[argl[0].lower()]['ed4']['eframe'].title()}```\nWe have collaborated with Keqing Bot\nFor frame testing use [Keqing Bot](https://top.gg/bot/772642704257187840), [Keqing Support](https://discord.gg/8pMnSqweut)",
                                        color=0x00FFB7)
                cembed4.set_thumbnail(url=f"{cdict[argl[0].lower()]['ed4']['url']}")
                cembed4.set_footer(text=f"Requested by {uid}")
                econtents.append(cembed4)
            pages = len(econtents)
            cur_page = 1
            message = await ctx.channel.send(embed=econtents[cur_page - 1])
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")
        
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"]
        
            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                    if str(reaction.emoji) == "➡️" and cur_page != pages:
                        cur_page += 1
                        await message.edit(embed=econtents[cur_page - 1])
                        await message.remove_reaction(reaction, user)
                    elif str(reaction.emoji) == "⬅️" and cur_page > 1:
                        cur_page -= 1
                        await message.edit(embed=econtents[cur_page - 1])
                        await message.remove_reaction(reaction, user)
                    else:
                        await message.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    return

        '''if 'ed4' not in cdict[argl[0].lower()].keys():
            await ctx.channel.send("Sorry I could not suggest frames for that character or it is not added yet.")
            return'''
        if argl[-1].lower() not in ["ed1", "ed2", "ed3", "ed4"]:
            await ctx.channel.send("Please mention the edition of the card")
            return
        if argl[-1].lower() == "ed4" and 'ed4' not in cdict[argl[0].lower()].keys():
            await ctx.channel.send("Sorry I could not suggest frames for that character or it is not added yet.")
            return
        cembed = discord.Embed(title="**Frame Suggestions**", description=f"**Character Name**: {cdict[argl[0].lower()]['cname'].title()} ({argl[-1].capitalize()})\n\n**Bit Frames**:\n```\n{cdict[argl[0].lower()][argl[-1].lower()]['bframe'].title()}```\n**Gem Frames**:\n```\n{cdict[argl[0].lower()][argl[-1].lower()]['gframe'].title()}```\n**Carousel Frames**:\n```\n{cdict[argl[0].lower()][argl[-1].lower()]['cframe'].title()}```\n**Event Frames**:\n```\n{cdict[argl[0].lower()][argl[-1].lower()]['eframe'].title()}```\nWe have collaborated with Keqing Bot\nFor frame testing use [Keqing Bot](https://top.gg/bot/772642704257187840), [Keqing Support](https://discord.gg/8pMnSqweut)", color=0x00FFB7)
        cembed.set_thumbnail(url=f"{cdict[argl[0].lower()][argl[-1].lower()]['url']}")
        cembed.set_footer(text=f"Requested by {uid}")
        await ctx.channel.send(embed=cembed)
        
        
def setup(bot):
    bot.add_cog(FrameSuggestion(bot))
