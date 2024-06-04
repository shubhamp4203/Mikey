from io import StringIO
import discord
from discord.ext import commands
from discord.ui import Button, View
from datetime import datetime
import asyncio
import aiohttp
import urllib.parse
from discord.ext import tasks, commands

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


class codetrace(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_get_url = "http://185.190.140.106:6969/api/trace/find/"
        self.api_post_url = "http://185.190.140.106:6969/api/trace"
        self.api_put_url = "http://185.190.140.106:6969/api/trace/hide/{code}"
        self.api_un_put_url = "http://185.190.140.106:6969/api/trace/unhide/{code}"
        self.form_data = {
          "card_name": None,
          "series": None,
          "code": None,
          "print": None,
          "edition": None,
          "scrappedAt": None,
        }
        self.snd_rep = {'e1': 0, 'e2' : 0, 'e3' : 0, 'e4' : 0 , 'e5' : 0, 'total' : 0}
        self.card_upd_lis = []
        self.traceruns = 0
        self.bot.card_count = 0
        self.vdelay = 0
        self.card_upd_to_api.start()
        self.total_upd_tsk.start()
        
    def cog_unload(self):
        self.card_upd_to_api.cancel()
        self.total_upd_tsk.cancel()

    async def dat_upd(self, cardname, seriesname, cardcode, card_print, ed):
        data = {
          "card_name": cardname,
          "series": seriesname,
          "code": cardcode.strip(),
          "print": card_print,
          "edition": ed,
          "scrappedAt": datetime.now(),
        }
        self.card_upd_lis.append(data)
        #print(data)
    
    async def snd_data_rep(self, data, resp_status = 200):
        send_channel = self.bot.get_channel(870275991883358278)
        aembed = discord.Embed(title="Cards Added", description=f"```py\n◈1    : {data[1]}\n◈2    : {data[2]}\n◈3    : {data[3]}\n◈4    : {data[4]}\nTotal : {data[1]+data[2]+data[3]+data[4]}\n```", color = 0x00FFB7 if resp_status==200 else 0xFF0000, timestamp=datetime.now())
        await send_channel.send(embed = aembed)
    
    async def snd_temp(self, data, resp_status = 200):
        send_channel = self.bot.get_channel(970241195378901052)
        aembed = discord.Embed(title="Card Added", description=f"```Name    : {data['card_name']}\nSeries  : {data['series']}\nCode    : {data['code']}\nPrint   : {data['print']}\nEdition : {data['edition']}```", color = 0x00FFB7 if resp_status==200 else 0xFF0000, timestamp=data['scrappedAt'])
        aembed.set_footer(text = f"{len(self.card_upd_lis)-1} left in queue")
        await send_channel.send(embed = aembed)
    
    @commands.command()
    @commands.is_owner()
    async def traced(self, ctx, new_v : int):
        if ctx.channel.type == discord.ChannelType.private:
            return
        if ctx.author.bot:
            return
        self.vdelay = new_v
        await ctx.reply(f"Delay set to `{new_v}`s")
    
    @commands.command()
    @commands.is_owner()
    async def tracecount(self, ctx):
        if ctx.channel.type == discord.ChannelType.private:
            return
        if ctx.author.bot:
            return
        await ctx.reply(f"`{self.traceruns}` runs.")
    
    @commands.command(name="trace", aliases=[], description = "Browse link below to get detailed info :``` **[READ TRACE DOC](https://docs.google.com/document/d/1CxnTPBCz__4iFmQL_hj4GeLfCiy5Qx_luVp3UBftIgM/edit?usp=drivesdk)**\n```\nTraces codes of karuta cards below 500 print.\n")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cadd(self, ctx, *, query = None):
        if ctx.channel.type == discord.ChannelType.private:
            return
        if ctx.author.bot:
            return
        if ctx.channel.id == 875275103238242365:
            await ctx.reply("Sorry you cannot use that command here!!")
            return
        if query == None:
            tembed = discord.Embed(title="Trace Stats", description=f"```py\n◈1 : {self.snd_rep['e1']:,}\n◈2 : {self.snd_rep['e2']:,}\n◈3 : {self.snd_rep['e3']:,}\n◈4 : {self.snd_rep['e4']:,}\n◈5 : {self.snd_rep['e5']:,}\nTotal : {self.snd_rep['total']:,}\n```")
            await ctx.reply(embed = tembed)
            return
        if any(i in query for i in ["??",]):
            await ctx.reply("No match found!")
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
            lembed = discord.Embed(title="Trace Result", description=f"\n{trace_dat_dict[cur_pagel]}\n", color=0x00FFB7)
            lembed.set_footer(text = f"Page: {cur_pagel} of {pagesl}")
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
            lembed = discord.Embed(title="Trace Result", description=f"\n{trace_dat_dict[cur_pagel]}\n", color=0x00FFB7)
            lembed.set_footer(text = f"Page: {cur_pagel} of {pagesl}")
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
            lembed = discord.Embed(title="Trace Result", description=f"\n{trace_dat_dict[cur_pagel]}\n", color=0x00FFB7)
            lembed.set_footer(text = f"Page: {cur_pagel} of {pagesl}")
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
            lembed = discord.Embed(title="Trace Result", description=f"\n{trace_dat_dict[cur_pagel]}\n", color=0x00FFB7)
            lembed.set_footer(text = f"Page: {cur_pagel} of {pagesl}")
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
        msg = await ctx.reply("Fetching Codes...")
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_get_url, data = {"filters" : query}) as resp:
                resp_dict =  await resp.json()
        self.traceruns += 1
        if (len(resp_dict.keys()) < 2):
            await msg.edit("No match found!")
            return
        tim_now = datetime.now().timestamp() * 1000
        resp_dict["cards"] = [card_x for card_x in resp_dict["cards"] if tim_now - card_x["scrappedAt"] > self.vdelay]
        resp_dict["total"] = len(resp_dict["cards"])
        if (resp_dict["total"] < 1):
            await msg.edit("No match found!")
            return
        t_pno = 1
        trace_dat_dict = {1:""}
        cn = 1 if resp_dict["total"] < 10 else 2
        for card_dat, cardno in zip(resp_dict["cards"], range(1, resp_dict["total"]+1)):
            if t_pno*10 < cardno:
                t_pno += 1
                trace_dat_dict[t_pno] = ""
                if t_pno == 10:
                    cn += 1
            try:
                pn = len(str(resp_dict["cards"][((cardno-1) - (cardno-1)%10 + 9) if ((cardno-1) - (cardno-1)%10 + 9) <= resp_dict["total"]-1 else resp_dict["total"]-1]['print']))
            except:
                pn = 3
            trace_dat_dict[t_pno] += f"`{cardno : <{cn}}` · `#{card_dat['print'] : <{pn}}` · `{'HIDDEN' if card_dat['isHidden'] else card_dat['code'] : >6}` · `◈{card_dat['edition']}` · {card_dat['series']} · **{card_dat['card_name']}**\n" 
        pagesl = len(trace_dat_dict.keys())
        cur_pagel = 1
        button1.callback = b1_callback
        button2.callback = b2_callback
        button3.callback = b3_callback
        button4.callback = b4_callback
        button1.disabled = True
        button2.disabled = True
        lembed = discord.Embed(title="Trace Result", description=f"\n{trace_dat_dict[cur_pagel]}\n", color=0x00FFB7)
        lembed.set_footer(text = f"Page: {cur_pagel} of {pagesl}")
        await msg.edit("",embed=lembed, view=view if pagesl>1 else None)
    
    @commands.command(name="tracehide", aliases=[], description = "")
    async def tracehide(self, ctx, *, query = None):
        if ctx.channel.type == discord.ChannelType.private:
            return
        if ctx.author.bot:
            return
        if ctx.channel.id == 875275103238242365:
            await ctx.reply("Sorry you cannot use that command here!!")
            return
        if not(ctx.message.reference):
            await ctx.reply("Please reply to the `kci` message of karuta bot")
            return
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if message.author.id != 646937666251915264:
            return
        if message.embeds[0].title != "Card Details" or message.embeds[0].description.startswith("Owned by"):
            await ctx.reply("Please reply to the `kci` message of karuta bot")
            return
        if datetime.timestamp(datetime.now())-datetime.timestamp(message.created_at) > 60:
            return
        card_print = int(message.embeds[0].description.split("\n")[0].split("·")[-4].replace(" `#", "").replace("`", ""))
        owner_id = int(message.embeds[0].description.split("Owned by <@")[1].split(">")[0])
        if ctx.author.id != owner_id:
            await ctx.reply("You do not own that card.")
            return
        if card_print>500:
            await ctx.reply("You cant hide 500+ print cards")
            return
        cardcode = message.embeds[0].description.split("\n")[0].split(" · ")[-6].split("`")[1]
        async with aiohttp.ClientSession() as session:
            async with session.put(self.api_put_url.format(code = cardcode), data = {"ownerID" : owner_id}) as resp:
                respp = resp.status
        await ctx.send(f"`{cardcode}` is hidden now.")
        
    @commands.command(name="traceunhide", aliases=[], description = "")
    async def traceunhide(self, ctx, *, query = None):
        if ctx.channel.type == discord.ChannelType.private:
            return
        if ctx.author.bot:
            return
        if ctx.channel.id == 875275103238242365:
            await ctx.reply("Sorry you cannot use that command here!!")
            return
        if not(ctx.message.reference):
            await ctx.reply("Please reply to the `kci` message of karuta bot")
            return
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if message.author.id != 646937666251915264:
            return
        if message.embeds[0].title != "Card Details" or 0:
            await ctx.reply("Please reply to the `kci` message of karuta bot")
            return
        if datetime.timestamp(datetime.now())-datetime.timestamp(message.created_at) > 60:
            return
        card_print = int(message.embeds[0].description.split("\n")[0].split("·")[-4].replace(" `#", "").replace("`", ""))
        owner_id = int(message.embeds[0].description.split("Owned by <@")[1].split(">")[0])
        if ctx.author.id != owner_id:
            await ctx.reply("You do not own the card.")
            return
        if card_print>500:
            return
        cardcode = message.embeds[0].description.split("\n")[0].split(" · ")[-6].split("`")[1]
        async with aiohttp.ClientSession() as session:
            async with session.put(self.api_un_put_url.format(code = cardcode)) as resp:
                respp = resp.status
        await ctx.send(f"`{cardcode}` is public now.")
    
    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id != 646937666251915264:
            return
        if not msg.embeds:
            return
        if msg.embeds[0].title == "Card Details":
            desp = msg.embeds[0].description.split("\n")
            if desp[0].startswith("Owned by"):
                card_print = int(desp[2].split("·")[2].replace(" `#", "").replace("`", ""))
                if card_print > 500:
                    return
                cardname = desp[2].split("·")[-1].replace(" **", "").replace("**", "").replace("~~", "")
                seriesname = desp[2].split(" · ")[-2].replace("~~", "")
                ed = int(desp[2].split(' · ')[-3].replace("`", "").replace("◈", ""))
                quer = f"c:{cardname} s:{seriesname} e:{ed} p:{card_print}"
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.api_get_url, data = {"filters" : quer}) as resp:
                        resp_dict =  await resp.json()
                if (len(resp_dict.keys()) > 1):
                    return
                cardcode = desp[2].split(" · ")[-6].split("`")[1]
                await self.dat_upd(cardname, seriesname, cardcode, card_print, ed)
            else:
                card_print = int(desp[0].split("·")[-4].replace(" `#", "").replace("`", ""))
                if card_print > 500:
                    return
                cardname = desp[0].split("·")[-1].replace(" **", "").replace("**", "").replace("~~", "")
                if "alias of" in cardname:
                    cardname = cardname.split("alias of")[1].replace(")*","").strip()
                seriesname = desp[0].split(" · ")[-2].replace("~~", "")
                ed = int(desp[0].split(" · ")[-3].replace("`", "").replace("◈", ""))
                quer = f"c:{cardname} s:{seriesname} e:{ed} p:{card_print}"
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.api_get_url, data = {"filters" : quer}) as resp:
                        resp =  await resp.json()
                if (len(resp.keys()) > 1):
                    return
                cardcode = desp[0].split(" · ")[-6].split("`")[1]
                await self.dat_upd(cardname, seriesname, cardcode, card_print, ed)
        elif msg.embeds[0].title == "Card Collection":
            desp = msg.embeds[0].description.split("\n")[2::]
            if desp[0] == "The list is empty.":
                return
            for c_line in desp:
                card_print = int(c_line.split('·')[-4].replace("`#", "").replace("`", ""))
                if card_print > 500:
                    continue
                cardname = c_line.split('·')[-1].replace(" **", "").replace("**", "").replace("~~", "")
                seriesname = c_line.split(' · ')[-2].replace("~~", "")
                ed = int(c_line.split(' · ')[-3].replace("`", "").replace("◈", ""))
                quer = f"c:{cardname} s:{seriesname} e:{ed} p:{card_print}"
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.api_get_url, data = {"filters" : quer}) as resp:
                        resp =  await resp.json()
                if (len(resp.keys()) > 1):
                    continue
                cardcode = c_line.split(' · ')[-6].split('`')[1]
                await self.dat_upd(cardname, seriesname, cardcode, card_print, ed)
            def me_check(msg_b,e_msg):
                return msg_b.id == msg.id
            while True:
                try:
                    msg_b,e_msg = await self.bot.wait_for('message_edit', timeout = 25 ,check = me_check)
                except:
                    return
                desp = e_msg.embeds[0].description.split("\n")[2::]
                if desp[0] == "The list is empty.":
                    return
                for c_line in desp:
                    card_print = int(c_line.split('·')[-4].replace("`#", "").replace("`", ""))
                    if card_print > 500:
                        continue
                    cardname = c_line.split('·')[-1].replace(" **", "").replace("**", "").replace("~~", "")
                    seriesname = c_line.split(' · ')[-2].replace("~~", "")
                    ed = int(c_line.split(' · ')[-3].replace("`", "").replace("◈", ""))
                    quer = f"c:{cardname} s:{seriesname} e:{ed} p:{card_print}"
                    async with aiohttp.ClientSession() as session:
                        async with session.post(self.api_get_url, data = {"filters" : quer}) as resp:
                            resp =  await resp.json()
                    if (len(resp.keys()) > 1):
                        continue
                    cardcode = c_line.split(' · ')[-6].split('`')[1]
                    await self.dat_upd(cardname, seriesname, cardcode, card_print, ed)
        else:
            return
    '''@commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id != 646937666251915264:
            return
        if msg.channel.id != 870275991883358278:
            return
        a = 'aagayionline:983800775459360768'
        await msg.add_reaction(a)
        chnl = self.bot.get_channel(870275991883358278)
        file = StringIO()
        file.write(str(msg.embeds[0].to_dict()))
        file.seek(0)
        await chnl.send(file=discord.File(fp=file, filename='out.txt'))'''


    @tasks.loop(seconds = 120.0)
    async def total_upd_tsk(self):
            async with aiohttp.ClientSession() as session:
                async with session.get("http://185.190.140.106:6969/api/trace/total") as resp:
                    resp_dict =  await resp.json()
            self.snd_rep = resp_dict
            self.bot.card_count = resp_dict['total']
    @tasks.loop(seconds = 10.0)
    async def card_upd_to_api(self):
        l_till = len(self.card_upd_lis)
        if l_till == 0:
            return
        #snd_rep = {1 : 0, 2 : 0, 3 : 0, 4 : 0 }
        status = 200
        for _ in range(l_till):
            data = self.card_upd_lis[0]
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_post_url, data=data) as resp:
                    resp_status =  resp.status
            if resp_status != 200:
                status = resp_status
            self.card_upd_lis.pop(0)
        #await self.snd_data_rep(snd_rep, status)

def setup(bot):
    bot.add_cog(codetrace(bot))
