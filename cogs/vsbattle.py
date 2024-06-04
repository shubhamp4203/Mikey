from PIL import Image
import discord
from discord.ext import commands, tasks
import requests
from io import BytesIO
import json
from discord.ui import Button, View



with open("vsbattledata.json", 'r') as f:
    vsbattledict = json.load(f)


def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def convert(time):
    pos = ["s","m","h","d"]
    time_dict = {"s": 1,"m": 60,"h": 3600,"d": 24*3600 }
    unit = time[-1]
    if unit not in pos:
        return -1
    try:
        timeVal = int(time[:-1])
    except:
        return -2

    return timeVal*time_dict[unit]

class Perview(discord.ui.View):
    def __init__(self,c1code=None, c2code=None):
        self.c1ode = c1code
        self.c2code = c2code
        super().__init__(timeout=None)

    @discord.ui.button(label="1️⃣", style=discord.ButtonStyle.gray, custom_id="1st vote")
    async def b1callback(self, button, interaction):
        if str(interaction.user.id) in vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][2]:
            vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][2].remove(str(interaction.user.id))
        vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][1].append(str(interaction.user.id))
        vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][1] = set(
            vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][1])
        vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][1] = list(
            vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][1])
        with open("vsbattledata.json", 'w') as f:
            json.dump(vsbattledict, f, indent=4)
        new_embed = discord.Embed(title=vsbattledict[str(interaction.guild.id)]['current_event'],
                                  description=f"**{self.c1ode}** - {len(vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][1])} Votes ({round((len(vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][1]) / (len(vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][1]) + len(vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][2]))) * 100)}%)\n**{self.c2code}** - {len(vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][2])} Votes ({round((len(vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][2]) / (len(vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][1]) + len(vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][2]))) * 100)}%)\n\nVoting time is <t:{vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][6]}:R>",
                                  color=0xFF0000)
        new_embed.set_image(url="attachment://banner.png")
        await interaction.response.edit_message(embed=new_embed, view=self)
        return

    @discord.ui.button(label="2️⃣", style=discord.ButtonStyle.gray, custom_id="2nd vote")
    async def b2callback(self, button, interaction):
        if str(interaction.user.id) in vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][1]:
            vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][1].remove(str(interaction.user.id))
        vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][2].append(str(interaction.user.id))
        vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][2] = set(
            vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][2])
        vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][2] = list(
            vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][2])
        with open("vsbattledata.json", 'w') as f:
            json.dump(vsbattledict, f, indent=4)
        new_embed = discord.Embed(title=vsbattledict[str(interaction.guild.id)]['current_event'],
                                  description=f"**{self.c1ode}** - {len(vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][1])} Votes ({round((len(vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][1]) / (len(vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][1]) + len(vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][2]))) * 100)}%)\n**{self.c2code}** - {len(vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][2])} Votes ({round((len(vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][2]) / (len(vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][1]) + len(vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][2]))) * 100)}%)\n\nVoting time is <t:{vsbattledict[str(interaction.guild.id)]['result'][str(interaction.message.id)][6]}:R>",
                                  color=0xFF0000)
        new_embed.set_image(url="attachment://banner.png")
        await interaction.response.edit_message(embed=new_embed, view=self)
        return


class Myview(discord.ui.View):
    def __init__(self,timeout=None):
        super().__init__(timeout=timeout)

class vsbattle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vs_upd.start()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(Perview())

    def cog_unload(self):
        self.vs_upd.cancel()

    async def resdec(self,gid, cid: int, mid: int):
        await self.bot.wait_until_ready()
        chnl = self.bot.get_channel(cid)
        msg = await chnl.fetch_message(mid)
        if len(vsbattledict[gid]['result'][str(mid)][1]) > len(vsbattledict[gid]['result'][str(mid)][2]):
            winner = vsbattledict[gid]['result'][str(mid)][4]
        elif len(vsbattledict[gid]['result'][str(mid)][1]) < len(vsbattledict[gid]['result'][str(mid)][2]):
            winner = vsbattledict[gid]['result'][str(mid)][5]
        else:
            winner=None

        if winner == None:
            resem = discord.Embed(title=f"**{vsbattledict[gid]['current_event']}**", description=f"The match ended with a draw.", color=0xFF0000)
            resem.set_image(url="attachment://banner.png")
            await msg.edit(embed = resem, view=None)
            return
        resem = discord.Embed(title=f"**{vsbattledict[gid]['current_event']}**",
                              description=f"The card **{winner}** won the match", color=0xFF0000)
        resem.set_image(url="attachment://banner.png")
        await msg.edit(embed=resem, view = None)
        return

    @tasks.loop(seconds=30)
    async def vs_upd(self):
        await self.bot.wait_until_ready()
        for gid in vsbattledict.keys():
            if 'result' in vsbattledict[gid]:
                for mid in vsbattledict[gid]['result'].copy().keys():
                    if int(vsbattledict[gid]['result'][mid][6]) - discord.utils.utcnow().timestamp() <= 5:
                        await self.resdec(gid, vsbattledict[gid]['result'][mid][0], vsbattledict[gid]['result'][mid][3])
                        del vsbattledict[gid]['result'][str(mid)]
        with open("vsbattledata.json", 'w') as f:
            json.dump(vsbattledict, f, indent=4)

    @commands.command(name="create-event")
    @commands.has_permissions(manage_guild=True)
    async def createevent(self, ctx, event_name):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if str(ctx.guild.id) in vsbattledict.keys():
            if vsbattledict[str(ctx.guild.id)]['current_event'] != None:
                but1 = Button(label="✔", style=discord.ButtonStyle.grey, custom_id="tick")
                but2 = Button(label="❌", style=discord.ButtonStyle.grey, custom_id="cross")
                view = Myview(timeout=10)
                view.add_item(but1)
                view.add_item(but2)

                async def b1callback(interaction):
                    if interaction.user.id != ctx.author.id:
                        await interaction.response.send_message("You  cannot use that!!", ephemeral=True)
                        return
                    vsbattledict[str(ctx.guild.id)] = {
                        'custom_banner': "https://i.imgur.com/5LoKFXSh.jpg",
                        'current_event': event_name, 'current_round': None}
                    with open("vsbattledata.json", "w") as f:
                        json.dump(vsbattledict, f, indent=4)
                    but1.style = discord.ButtonStyle.green
                    but1.disabled = True
                    but2.disabled = True
                    await interaction.response.edit_message(view=view)
                    await ctx.reply(f"Event `{event_name}` successfully created")
                    return

                async def b2callback(interaction):
                    if interaction.user.id != ctx.author.id:
                        await interaction.response.send_message("You  cannot use that!!", ephemeral=True)
                        return
                    but2.style = discord.ButtonStyle.red
                    but1.disabled = True
                    but2.disabled = True
                    await interaction.response.edit_message(view=view)
                    return

                but1.callback = b1callback
                but2.callback = b2callback
                warning_embed = discord.Embed(title="WARNING!!",
                                              description=f"The event **{vsbattledict[str(ctx.guild.id)]['current_event']}** is already in progress. Do you still want to start a new event? By doing so the all the data will be reset. React with ✔ to continue and ❌ to stop.",
                                              color=0xFF0000)
                await ctx.reply(embed=warning_embed, view=view)
                return
            else:
                vsbattledict[str(ctx.guild.id)]['current_event'] = event_name
                with open("vsbattledata.json", 'w') as f:
                    json.dump(vsbattledict, f, indent=4)
                await ctx.reply(f"Event `{event_name}` successfully created")
                return
        else:
            vsbattledict[str(ctx.guild.id)] = {
                'custom_banner': "https://i.imgur.com/5LoKFXSh.jpg",
                'current_event': event_name, 'current_round': None}
            with open("vsbattledata.json", "w") as f:
                json.dump(vsbattledict, f, indent=4)
            await ctx.reply(f"Event **{event_name}** successfully created")

    @commands.command(name="setbanner", aliases=['sb'])
    @commands.has_permissions(manage_guild=True)
    async def bannerset(self, ctx, banner_url):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if banner_url.endswith("png") or banner_url.endswith("jpg") or banner_url.endswith("jpeg"):
            if str(ctx.guild.id) not in vsbattledict.keys():
                vsbattledict[str(ctx.guild.id)] = {'custom_banner': banner_url, 'current_event': None,
                                                   'current_round': None}
                with open('vsbattledata.json', 'w') as f:
                    json.dump(vsbattledict, f, indent=4)
                await ctx.reply("Custom banner set successfully!")
                return
            vsbattledict[str(ctx.guild.id)]['custom_banner'] = banner_url
            with open('vsbattledata.json', 'w') as f:
                json.dump(vsbattledict, f, indent=4)
            await ctx.reply("Custom banner set successfully!")
        else:
            await ctx.reply("Invalid banner url.")

    @commands.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def addChar(self, ctx):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if str(ctx.guild.id) not in vsbattledict.keys() or vsbattledict[str(ctx.guild.id)]['current_event'] == None:
            await ctx.reply("Please first create an event using `m.create-event` command.")
            return
        if not ctx.message.reference:
            await ctx.reply("Please reply to kv message of karuta bot.")
            return
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if message.author.id == 646937666251915264 and message.embeds[0].title == "Card Details":
            card_code = message.embeds[0].description.split("·")[0].split("\n\n")[1].split("`")[1]
            card_url = message.embeds[0].image.url
            vsbattledict[str(ctx.guild.id)][card_code] = card_url
            with open("vsbattledata.json", 'w') as f:
                json.dump(vsbattledict, f, indent=4)
            await ctx.channel.send(f"Added the image for the card **{card_code}**")

    @commands.command(name='start-round')
    @commands.has_permissions(manage_guild=True)
    async def  startround(self, ctx, round_no, votingtime):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if str(ctx.guild.id) not in vsbattledict.keys() or vsbattledict[str(ctx.guild.id)]['current_event'] == None:
            await ctx.reply("Please first create an event using `m.create-event` command.")
            return
        voting_time = convert(votingtime)
        if voting_time == -2:
            await ctx.reply("Please use the correct format for time.")
            return
        elif voting_time == -1:
            await ctx.reply("Please use the correct format for time.")
            return
        elif voting_time > 86400:
            await ctx.reply("Sorry maximum voting time is 1 Day or 24 Hours currently.")
            return
        elif voting_time < 900:
            await ctx.reply("Sorry minimum voting time is 15 Minutes")
            return
        else:
            pass
        vsbattledict[str(ctx.guild.id)]['current_round'] = round_no
        vsbattledict[str(ctx.guild.id)]['result'] = {}
        vsbattledict[str(ctx.guild.id)]['votingtime'] = voting_time
        with open("vsbattledata.json", 'w') as f:
            json.dump(vsbattledict, f, indent=4)
        await ctx.reply(f"**Round-{round_no}** is live now.")

    @commands.command(name="vs")
    @commands.has_permissions(manage_guild=True)
    async def vsGenerator(self, ctx, cardcode1, cardcode2):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if str(ctx.guild.id) not in vsbattledict.keys() or vsbattledict[str(ctx.guild.id)]['current_event'] == None:
            await ctx.reply("Please first create an event using `m.create-event` command.")
            return
        if vsbattledict[str(ctx.guild.id)]['current_round'] == None:
            await ctx.reply("Please start the round first using `m.start-round` command")
            return
        view = Perview(cardcode1, cardcode2)
        bannerurl = vsbattledict[str(ctx.guild.id)]['custom_banner']
        r = requests.get(bannerurl, stream=True)
        s1 = requests.get(vsbattledict[str(ctx.guild.id)][cardcode1], stream=True)
        s2 = requests.get(vsbattledict[str(ctx.guild.id)][cardcode2], stream=True)
        banner = Image.open(r.raw)
        card1 = Image.open(s1.raw)
        card2 = Image.open(s2.raw)
        banner = banner.resize((885,605))
        banner.paste(card1, (75,100), mask=card1)
        banner.paste(card2, (536,100), mask=card2)
        bytes = BytesIO()
        banner.save(bytes, format="PNG")
        bytes.seek(0)
        dfile = discord.File(bytes, filename="banner.png")
        send_embed = discord.Embed(title=vsbattledict[str(ctx.guild.id)]['current_event'], description=f"**{cardcode1}** - 0 Votes (0%)\n**{cardcode2}** - 0 Votes (0%)\n\nVoting time is <t:{round((discord.utils.utcnow().timestamp() + vsbattledict[str(ctx.guild.id)]['votingtime']))}:R>", color=0xFF0000)
        send_embed.set_image(url="attachment://banner.png")
        await ctx.message.delete()
        msg = await ctx.channel.send(file=dfile, embed=send_embed, view=view)
        vsbattledict[str(ctx.guild.id)]['result'][str(msg.id)] = [ctx.channel.id, [], [], msg.id, cardcode1, cardcode2, round((discord.utils.utcnow().timestamp() + vsbattledict[str(ctx.guild.id)]['votingtime']))]
        with open("vsbattledata.json", 'w') as f:
            json.dump(vsbattledict, f, indent=4)

    @commands.command(name="end-event")
    async def endevent(self, ctx):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if vsbattledict[str(ctx.guild.id)]['current_event'] == None:
            await ctx.reply("There is no ongoing event in this server.")
            return
        warembed = discord.Embed(title="**WARNING!!**", description=f"The event **{vsbattledict[str(ctx.guild.id)]['current_event']}** is in progress. Proccessing this command will reset all the data. Do you still wish to continue?", color=0xFF0000)
        view = Myview(timeout=15)
        b1 = Button(label="✔", style=discord.ButtonStyle.gray, custom_id="tick")
        b2 = Button(label="❌", style=discord.ButtonStyle.gray, custom_id="cross")
        view.add_item(b1)
        view.add_item(b2)

        async def b1callback(interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("You  cannot use that!!", ephemeral=True)
                return
            b1.style = discord.ButtonStyle.green
            b1.disabled = True
            b2.disabled = True
            await interaction.response.edit_message(view=view)
            await interaction.followup.send(f"The event `{vsbattledict[str(ctx.guild.id)]['current_event']}` ended successfully")
            vsbattledict[str(ctx.guild.id)] = {'custom_banner': "https://i.imgur.com/5LoKFXSh.jpg", 'current_event': None, 'current_round': None, 'result': {}}
            with open("vsbattledata.json", 'w') as f:
                json.dump(vsbattledict, f, indent=4)
            return

        async def b2callback(interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("You  cannot use that!!", ephemeral=True)
                return
            b2.style = discord.ButtonStyle.red
            b2.disabled = True
            b1.disabled = True
            await interaction.response.edit_message(view=view)
            return
        b1.callback = b1callback
        b2.callback = b2callback

        await ctx.reply(embed=warembed, view=view)

def setup(bot):
    bot.add_cog(vsbattle(bot))
