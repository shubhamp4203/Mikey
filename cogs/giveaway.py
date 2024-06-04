import discord
from discord.ext import commands, tasks
import random
import asyncio
import re
import datetime
import typing

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

async def invites(ctx, user):
    totalInvites = 0
    for i in await ctx.guild.invites():
        if i.inviter == user:
            totalInvites += i.uses
    return totalInvites

def stohr(s_econds):
    days = s_econds//(24*3600)
    s_econds %= (24*3600)
    hr = s_econds//3600
    s_econds %= 3600
    min = s_econds//60
    s_econds %= 60
    s_econds,hr,min,days = str(s_econds)+"s",str(hr)+"hr ",str(min)+"min ", str(days)+"d "
    return days+hr+min+s_econds



class Giveaway(commands.Cog):
    """
    Advanced giveaway system for your server. It can last upto a month.
    """
    
    def __init__(self,bot):
        self.bot = bot
        self.cancelled = False
        self.ecolor = 0x00FFB7
        self.support = "\n\n[Support Server](https://discord.gg/dWttazRJ5f)"
        self.give_upd.start()
        
    def cog_unload(self):
        self.give_upd.stop()

    async def ginvites(self, guild, user):
        totalInvites = 0
        for i in await guild.invites():
            if i.inviter == user:
                totalInvites += i.uses
        return totalInvites

    def givedel_s(self, guildid,id_):
        sd_v = self.bot.dfread("servers_dat")
        for i in sd_v[guildid]["giveaways"]:
            if i[1] == id_:
                indx = sd_v[guildid]["giveaways"].index(i)
                break
        sd_v[guildid]["giveaways"].pop(indx)
        self.bot.dfwrite("servers_dat",sd_v)
        if self.bot.debug:
            return
        temp_doc = {"giveaways" : sd_v[guildid]["giveaways"]}
        self.bot.serverdat_obj.update_one({"_id" : int(guildid)}, {"$set" : temp_doc})

    async def invitesg(self, guild, user):
        totalInvites = 0
        for i in await guild.invites():
            if i.inviter == user:
                totalInvites += i.uses
        return totalInvites

    async def giveaway_roll(self, guildid, timeleft, channel_id, id_: int, delta):
        if timeleft<0:
            timeleft = 0
        timeleft = 0
        await asyncio.sleep(timeleft)
        try:
            clear_data = False
            try:
                channel = self.bot.get_channel(channel_id)
                msg = await channel.fetch_message(id_)
                if "Cancelled" in msg.embeds[0].to_dict()["title"]:
                    clear_data = True
            except:
                clear_data = True
            if clear_data:
                self.givedel_s(str(guildid), id_)
                return
            guild = self.bot.get_guild(int(guildid))
            users = await msg.reactions[0].users().flatten()
            if self.bot.user in users:
                users.pop(users.index(self.bot.user))
            users = list(set(users))
            desc = msg.embeds[0].to_dict()["title"][2::]
            description = msg.embeds[0].description
            winner_m = ""
            extentry = 0
            if msg.embeds[0].description:
                extentry = int(description.split("\n\n")[0].split("x")[0].split(" ")[-1])
                if extentry>1 :
                    for user1 in guild.premium_subscribers:
                        if user1 in users:
                            for _ in range(extentry-1):
                                users.append(user1)
                """if len(description.split("\n\n")) > 1:
                    min_invs =  int(description.split("\n\n")[1].split(":")[-1].split(" ")[1])
                    for user1 in users:
                        usrinvs = await self.ginvites(guild, user1)
                        if usrinvs < min_invs:
                            users.pop(users.index(user1))"""
            field_n = msg.embeds[0].fields[0].name
            users_n = users
            if 'Winners' in field_n:
                field_v = int(msg.embeds[0].fields[0].value)
                usr_count = len(users_n)
                for win in range(field_v):
                    if usr_count == 0:
                        break
                    winner_p = random.choice(users_n)
                    winner_m += winner_p.mention + ("" if win==(field_v-1) or usr_count == 0 else ", ")
                    users_n.pop(users_n.index(winner_p))
                    usr_count -= 1
            users = await msg.reactions[0].users().flatten()
            if self.bot.user in users:
                users.pop(users.index(self.bot.user))
            users = list(set(users))
            if extentry>1 :
                for user1 in guild.premium_subscribers:
                    if user1 in users:
                        for _ in range(extentry-1):
                            users.append(user1)
            if len(users) <= 0:
                emptyEmbed = discord.Embed(title=f"🎁 {desc}", colour = self.ecolor, description=description)
                if msg.embeds[0].image:
                    emptyEmbed.set_image(url = msg.embeds[0].image.url)
                emptyEmbed.set_footer(text="No one won the Giveaway." + " | Giveaway Ended")
                await msg.edit(embed=emptyEmbed)
            if len(users) > 0:
                winner = random.choice(users).mention
                if winner_m != "":
                    winner = winner_m
                winnerEmbed = discord.Embed(title=f"🎁 {desc}",
                                    colour=self.ecolor, description=description)
                winnerEmbed.add_field(name=f"Congratulations On Winning {desc}", value=winner)
                foo_tr = msg.embeds[0].to_dict()["footer"]["text"]
                if "Giveaway Ended" in foo_tr:
                    foo_tr = foo_tr.split(" | ")[0]
                if msg.embeds[0].image:
                    winnerEmbed.set_image(url = msg.embeds[0].image.url)
                winnerEmbed.add_field(name="Ended At : ", value=f"<t:{delta}:R> (<t:{delta}:F>)")
                winnerEmbed.set_footer(text=foo_tr + " | Giveaway Ended")
                linkEmbed = discord.Embed(title = "Giveaway", description = f"**[{desc}]({msg.jump_url})**", colour = self.ecolor)
                await msg.edit(embed=winnerEmbed)
                await msg.channel.send(winner+", you won **"+desc.strip()+"**", embed = linkEmbed)
            self.givedel_s(str(guildid), id_)
            return
        except Exception as e:
            if self.bot.debug:
                raise e
            try:
                self.givedel_s(str(guildid), id_)
            except Exception as e:
                if self.bot.debug:
                    raise e
                pass
            return

    @tasks.loop(seconds=10)
    async def give_upd(self):
        sd_v = self.bot.dfread("servers_dat")
        for guildid in sd_v.keys():
            if "giveaways" in sd_v[guildid]:
                for ga in sd_v[guildid]["giveaways"]:
                    if ga[0] - discord.utils.utcnow().timestamp() <= 2:
                        try:
                            await self.giveaway_roll(guildid, round(ga[0]-discord.utils.utcnow().timestamp()), ga[2], ga[1], ga[0])
                        except Exception as e:
                            if self.bot.debug:
                                raise e
                            pass


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.emoji) != "🎉":
            return
        try:
            guild = self.bot.get_guild(payload.guild_id)
            reactchannel = guild.get_channel(payload.channel_id)
            user = await guild.fetch_member(payload.user_id)
            message = await reactchannel.fetch_message(payload.message_id)
        except:
            return
        if message.author.id != self.bot.user.id:
            return
        if not(message.embeds):
            return
        try:
            title = message.embeds[0].to_dict()["title"]
            if not(title.startswith("🎁")):
                return
            foot_er = message.embeds[0].to_dict()["footer"]["text"]
            if "Giveaway Ended" in foot_er or "No one won the Giveaway." in foot_er:
                return
        except:
            return
        try:
            desc = message.embeds[0].to_dict()["description"]
        except:
            return
        if len(desc.split("\n\n")) > 1:
            min_invs =  int(desc.split("\n\n")[1].split(":")[-1].split(" ")[1])
        else:
            min_invs = 0
        if len(desc.split("\n\n")) > 1 and min_invs > 0:
            try:
                guild = await self.bot.fetch_guild(payload.guild_id)
                usrinvs = await self.invitesg(guild,user)
                if usrinvs >= min_invs:
                    dmembed = discord.Embed(colour = self.ecolor, title = "🎁 Giveaway Entry Confirmed", description = f"**Gift Items** : {title[2::]}"+"\n\n"+desc+self.support)
                    dmembed.set_footer(text="You successfully participated in this giveaway.")
                    await user.send(embed = dmembed)
                else:
                    dmembed = discord.Embed(colour = 0xFF0000, title = "❌ Giveaway Entry Denied", description = f"**Gift Items** :{title[2::]}\nMinimum Invites required : `{min_invs}`\nYour Invites : `{usrinvs}`"+self.support)
                    dmembed.set_footer(text="You cannot participate in this giveaway.")
                    await user.send(embed = dmembed)
                    await message.remove_reaction("🎉", user)
            except:
                return
        else:
            try:
                dmembed = discord.Embed(colour = self.ecolor, title = "🎁 Giveaway Entry Confirmed", description = f"**Gift Items** : {title[2::]}"+"\n\n"+desc+self.support)
                dmembed.set_footer(text="You successfully participated in this giveaway.")
                await user.send(embed = dmembed)
            except:
                return
        return
    
    @commands.command(name="giveaway", aliases=["gcreate"])
    @commands.has_permissions(manage_guild=True)
    async def create_giveaway(self, ctx):
        #Ask Questions
        embed = discord.Embed(title="Giveaway !",
                      description="**Time for a new Giveaway. Answer the following questions in 25 seconds each for the Giveaway.**",
                      color=self.ecolor)
        ab_msg = await ctx.send(embed=embed)
        questions=["**In Which channel do you want to host the giveaway?**",
                   "**For How long should the Giveaway be hosted ? type number followed (s|m|h|d)**",
                   "**What is the Prize?**", "**Number of winners**", "**Booster entries (y/n)**"]
        answers = []
        #Check Author
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        for i, question in enumerate(questions):
            embed = discord.Embed(title=f"Question {i+1}",
                          description=question)
            qmsg = await ctx.send(embed=embed)
            try:
                message = await self.bot.wait_for('message', timeout=25, check=check)
            except TimeoutError:
                await ctx.send("You didn't answer the questions in Time")
                return
            if i == 0:
                await ab_msg.delete()
            await qmsg.delete()
            answers.append(message.content)
        #Check if Channel Id is valid
        try:
            channel_id = int(answers[0][2:-1])
        except:
            await ctx.send("Invalid channel.")
            return
        channel = self.bot.get_channel(channel_id)
        if channel not in ctx.guild.channels:
            await ctx.send("Invalid channel.")
            return
        time = convert(answers[1])
        #Check if Time is valid
        if time == -1:
            await ctx.send("The Time format was wrong.")
            return
        elif time == -2:
            await ctx.send("The Time was not conventional number.")
            return
        elif time > 2628003:
            await ctx.send("Cannot host giveaway of more than a month/30 days.")
            return
        elif time < 10: return await ctx.send("Cannot host giveaway of less than 10 seconds.")
        try:
            int(answers[3])
        except:
            await ctx.send("Invalid no. of winners.")
            return
        prize = answers[2]
        time -= 1
        description = ""
        
        boo = answers[4].lower()
        if boo != "y" and boo != "n":
            return await ctx.send("Please provide valid option for booster entried (y/n)")
        if boo == "y":
            qmsg = await ctx.send("How many extra entries will the boosters get? (Must be between 2 and 10)")
            try:
                message = await self.bot.wait_for('message', timeout=25, check=check)
            except TimeoutError:
                await ctx.send("You didn't answer the question in Time")
                return
            try:
                booX = int(message.content)
            except:
                return await ctx.send("Invalid no. of extra entries.")
            if (booX > 10) or (booX < 2):
                return await ctx.send("Must be between 2 and 10")
            
            description = f"<a:booster:865177646483374080> Server booster gets {booX}x entries."
        await ctx.send(f"Your giveaway will be hosted in {channel.mention} and will last for {answers[1]}")
        
        delta = round((discord.utils.utcnow() + datetime.timedelta(seconds=time)).timestamp())
        e_url = ""
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', prize)
        for url in urls:
            if url.endswith(".png") or url.endswith(".jpg") or url.endswith(".webp"):
                e_url = url
                break
        embed = discord.Embed(title=f"🎁 {prize.replace(e_url, '')}",
                    colour=self.ecolor, description=description)
        if int(answers[3]) > 0:
            embed.add_field(name = 'Winners : ', value = str(answers[3]), inline = True)
        embed.add_field(name = 'Time Remaining : ', value = f'<t:{delta}:R> (<t:{delta}:F>)', inline = True)
        if e_url:
            embed.set_image(url=e_url)
        embed.set_footer(text=f"By reacting, you agree to being DMed.\nHosted by : {ctx.author}")
        newMsg = await channel.send(embed=embed)
        await newMsg.add_reaction("🎉")
        sd_v = self.bot.dfread("servers_dat")
        if "giveaways" not in sd_v[str(ctx.guild.id)]:
            sd_v[str(ctx.guild.id)]["giveaways"] = []
        sd_v[str(ctx.guild.id)]["giveaways"].append([delta,newMsg.id,channel_id])
        self.bot.dfwrite("servers_dat",sd_v)
        if self.bot.debug:
            return
        temp_doc = {"giveaways" : sd_v[str(ctx.guild.id)]["giveaways"]}
        self.bot.serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$set" : temp_doc})

    
    @commands.command(name="quickgiveaway", aliases=["gquick", "gstart", "giveawaystart"], description="Start a quick giveaway by providing <time>, [winners] and <prize>.\nWords in <> are required arguments and words in [] are optional.")
    @commands.has_permissions(manage_guild=True)
    async def quick_giveaway(self, ctx, time, winners: typing.Optional[int] = 1, *, prize):
        time = convert(time)
        #Check if Time is valid
        if time == -1:
            await ctx.send("The Time format was wrong.")
            return
        elif time == -2:
            await ctx.send("The Time was not conventional number.")
            return
        elif time > 2628003:
            await ctx.send("Cannot host giveaway of more than a month/30 days.")
            return
        elif time < 10: return await ctx.send("Cannot host giveaway of less than 10 seconds.")
        time -= 1
        
        if winners < 1: return await ctx.send("The number of winners must be a positive number.")
        
        delta = round((discord.utils.utcnow() + datetime.timedelta(seconds=time)).timestamp())
        e_url = ""
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', prize)
        for url in urls:
            if url.endswith(".png") or url.endswith(".jpg") or url.endswith(".webp"):
                e_url = url
                break
        embed = discord.Embed(title=f"🎁 {prize.replace(e_url, '')}",
                    colour=self.ecolor)
        embed.add_field(name = 'Winners : ', value = str(winners), inline = True)
        embed.add_field(name = 'Time Remaining : ', value = f'<t:{delta}:R> (<t:{delta}:F>)', inline = True)
        if e_url:
            embed.set_image(url=e_url)
        embed.set_footer(text=f"By reacting, you agree to being DMed.\nHosted by : {ctx.author}")
        newMsg = await ctx.send(embed=embed)
        await newMsg.add_reaction("🎉")
        sd_v = self.bot.dfread("servers_dat")
        if "giveaways" not in sd_v[str(ctx.guild.id)]:
            sd_v[str(ctx.guild.id)]["giveaways"] = []
        sd_v[str(ctx.guild.id)]["giveaways"].append([delta,newMsg.id,ctx.channel.id])
        self.bot.dfwrite("servers_dat",sd_v)
        if self.bot.debug:
            return
        temp_doc = {"giveaways" : sd_v[str(ctx.guild.id)]["giveaways"]}
        self.bot.serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$set" : temp_doc})
    
    
    @commands.command(name="reroll", aliases=["giftreroll", "giveawayreroll"])
    @commands.has_permissions(manage_guild=True)
    async def giveaway_reroll(self, ctx, channel : discord.TextChannel, id_: int):
        try:
            msg = await channel.fetch_message(id_)
        except:
            await ctx.send("The channel or ID mentioned was incorrect.")
            return
        if not(msg.embeds):
            return
        if not(msg.embeds[0].to_dict()["title"].startswith("🎁")):
            return
        desc = msg.embeds[0].to_dict()["title"][2::]
        if "Cancelled" in desc:
            await ctx.send("Cannot reroll a cancelled giveaway.")
            return
        users = await msg.reactions[0].users().flatten()
        if self.bot.user in users:
            users.pop(users.index(self.bot.user))
        users = list(set(users))
        description = msg.embeds[0].description
        if description:
            if len(description.split("\n\n")) > 1:
                min_invs =  int(description.split("\n\n")[1].split(":")[-1].split(" ")[1])
                for user1 in users:
                    usrinvs = await invites(ctx, user1)
                    if usrinvs < min_invs:
                        users.pop(users.index(user1))
            extentry = int(description.split("\n\n")[0].split("x")[0].split(" ")[-1])
            if extentry>1 :
                for user1 in ctx.guild.premium_subscribers:
                    if user1 in users:
                        for _ in range(extentry-1):
                            users.append(user1)
        foo_tr_temp = msg.embeds[0].to_dict()["footer"]["text"]
        if len(users) <= 0:
            emptyEmbed = discord.Embed(title=f"🎁 {desc}", colour = self.ecolor, description=description)
            if msg.embeds[0].image:
                emptyEmbed.set_image(url = msg.embeds[0].image.url)
            emptyEmbed.set_footer(text="No one won the Giveaway." + " | Giveaway Ended")
            await msg.edit(embed=emptyEmbed)
            return
        if len(users) > 0:
            winner = random.choice(users)
            winnerEmbed = discord.Embed(title=f"🎁 {desc}",
                                colour=self.ecolor, description=description)
            winnerEmbed.add_field(name=f"Congratulations On Winning {desc}", value=winner.mention)
            winnerEmbed.add_field(name=f"Ended At : ", value=f"<t:{round(ctx.message.created_at.timestamp())}:R> (<t:{round(ctx.message.created_at.timestamp())}:F>)")
            foo_tr = msg.embeds[0].to_dict()["footer"]["text"]
            if "Giveaway Ended" in foo_tr:
                foo_tr = foo_tr.split(" | ")[0]
            if msg.embeds[0].image:
                winnerEmbed.set_image(url = msg.embeds[0].image.url)
            winnerEmbed.set_footer(text=foo_tr + " | Giveaway Ended")
            linkEmbed = discord.Embed(title = "Giveaway", description = f"**[{desc}]({msg.jump_url})**", colour = self.ecolor)
            await msg.edit(embed=winnerEmbed)
            await msg.channel.send(winner.mention+", you won **"+desc+"**", embed = linkEmbed)
            return
        if "Giveaway Ended" not in foo_tr_temp:
            sd_v = self.bot.dfread("servers_dat")
            indx = None
            for i in sd_v[str(ctx.guild.id)]["giveaways"]:
                if i[1] == id_:
                    indx = sd_v[str(ctx.guild.id)]["giveaways"].index(i)
                    break
            if indx == None:
                return
            sd_v[str(ctx.guild.id)]["giveaways"].pop(indx)
            self.bot.dfwrite("servers_dat",sd_v)
            if self.bot.debug:
                return
            temp_doc = {"giveaways" : sd_v[str(ctx.guild.id)]["giveaways"]}
            self.bot.serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$set" : temp_doc})

    @commands.command(name="gdel", aliases = ["gacancel", "gadel"])
    @commands.has_permissions(manage_guild=True)
    async def giveaway_stop(self, ctx, channel : discord.TextChannel, id_: int):
        try:
            msg = await channel.fetch_message(id_)
            newEmbed = discord.Embed(title="Giveaway Cancelled", description="This giveaway has been cancelled!", colour = self.ecolor)
            await msg.edit(embed=newEmbed)
        except:
            pass
        try:
            sd_v = self.bot.dfread("servers_dat")
            indx = None
            for i in sd_v[str(ctx.guild.id)]["giveaways"]:
                if i[1] == id_:
                    indx = sd_v[str(ctx.guild.id)]["giveaways"].index(i)
                    break
            if indx != None:
                sd_v[str(ctx.guild.id)]["giveaways"].pop(indx)
                self.bot.dfwrite("servers_dat",sd_v)
            if not self.bot.debug:
                temp_doc = {"giveaways" : sd_v[str(ctx.guild.id)]["giveaways"]}
                self.bot.serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$set" : temp_doc})
            await ctx.send("Giveaway deleted successfully.")
        except Exception as e:
            await ctx.send("Giveaway not found or deleted already.")

    
    
    
    
    
    
    
    
    
        
    
    
    @commands.command(name="premmium-giveaway", aliases=["premiumgiveaway", "premgiveaway", "premgw"])
    @commands.has_permissions(manage_guild=True)
    async def premium_giveaway(self, ctx):
        #Ask Questions
        embed = discord.Embed(title="Giveaway !",
                      description="**Time for a new Giveaway. Answer the following questions in 25 seconds each for the Giveaway.**",
                      color=self.ecolor)
        ab_msg = await ctx.send(embed=embed)
        questions=["**In Which channel do you want to host the giveaway?**",
                   "**For How long should the Giveaway be hosted ? type number followed (s|m|h|d)**",
                   "**What is the Prize?**", "**Number of winners**", "**Booster entries (y/n)**"]
        answers = []
        #Check Author
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        for i, question in enumerate(questions):
            embed = discord.Embed(title=f"Question {i+1}",
                          description=question)
            qmsg = await ctx.send(embed=embed)
            try:
                message = await self.bot.wait_for('message', timeout=25, check=check)
            except TimeoutError:
                await ctx.send("You didn't answer the questions in Time")
                return
            if i == 0:
                await ab_msg.delete()
            await qmsg.delete()
            answers.append(message.content)
        #Check if Channel Id is valid
        try:
            channel_id = int(answers[0][2:-1])
        except:
            await ctx.send("Invalid channel.")
            return
        channel = self.bot.get_channel(channel_id)
        time = convert(answers[1])
        #Check if Time is valid
        if time == -1:
            await ctx.send("The Time format was wrong.")
            return
        elif time == -2:
            await ctx.send("The Time was not conventional number.")
            return
        elif time > 2628003:
            await ctx.send("Cannot host giveaway of more than a month/30 days.")
            return
        elif time < 10: return await ctx.send("Cannot host giveaway of less than 10 seconds.")
        try:
            int(answers[3])
        except:
            await ctx.send("Invalid no. of winners.")
            return
        prize = answers[2]
        time -= 1
        description = ""
        
        boo = answers[4].lower()
        if boo != "y" and boo != "n":
            return await ctx.send("Please provide valid option for booster entried (y/n)")
        if boo == "y":
            qmsg = await ctx.send("How many extra entries will the boosters get? (Must be between 2 and 10)")
            try:
                message = await self.bot.wait_for('message', timeout=25, check=check)
            except TimeoutError:
                await ctx.send("You didn't answer the question in Time")
                return
            try:
                booX = int(message.content)
            except:
                return await ctx.send("Invalid no. of extra entries.")
            if (booX > 10) or (booX < 2):
                return await ctx.send("Must be between 2 and 10")
            
            description = f"<a:booster:865177646483374080> Server booster gets {booX}x entries."
        await ctx.send(f"Your giveaway will be hosted in {channel.mention} and will last for {answers[1]}")
        
        delta = round((discord.utils.utcnow() + datetime.timedelta(seconds=time)).timestamp())
        e_url = ""
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', prize)
        for url in urls:
            if url.endswith(".png") or url.endswith(".jpg") or url.endswith(".webp"):
                e_url = url
                break
        embed = discord.Embed(title=f"🎁 {prize.replace(e_url, '')}",
                    colour=self.ecolor, description=description)
        if int(answers[3]) > 0:
            embed.add_field(name = 'Winners : ', value = str(answers[3]), inline = True)
        embed.add_field(name = 'Time Remaining : ', value = f'<t:{delta}:R> (<t:{delta}:F>)', inline = True)
        if e_url:
            embed.set_image(url=e_url)
        embed.set_footer(text=f"By reacting, you agree to being DMed.\nHosted by : {ctx.author}")
        newMsg = await channel.send(embed=embed)
        await newMsg.add_reaction("🎉")
        sd_v = self.bot.dfread("servers_dat")
        if "giveaways" not in sd_v[str(ctx.guild.id)]:
            sd_v[str(ctx.guild.id)]["giveaways"] = []
        sd_v[str(ctx.guild.id)]["giveaways"].append([delta,newMsg.id,channel_id])
        self.bot.dfwrite("servers_dat",sd_v)
        if self.bot.debug:
            return
        temp_doc = {"giveaways" : sd_v[str(ctx.guild.id)]["giveaways"]}
        self.bot.serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$set" : temp_doc})
    
    
    
    
    
    
def setup(bot):
    bot.add_cog(Giveaway(bot))
