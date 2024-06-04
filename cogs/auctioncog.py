import json
from dotenv import load_dotenv
import discord
from discord.ext import commands
import certifi
import os
from pymongo import MongoClient
import string
import random

load_dotenv()

def dfread(df_type):
    with open(f'./{df_type}.json', 'r') as sd :
        sd_v = json.load(sd)
    return sd_v

def dfwrite(df_type,dat):
    with open(f'./{df_type}.json', 'w') as sd :
        json.dump(dat, sd)

c_str = os.getenv("CONNECTION_STRING")
ca = certifi.where()
serverdat_obj = MongoClient(c_str, tlsCAFile=ca).mickeydb.serverdat

class auction(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.ecolor = 0x00FFB7
    
    @commands.command(name = 'set-auction')
    @commands.has_permissions(administrator=True)
    async def setauc(self,ctx):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if not(ctx.message.author.guild_permissions.administrator):
            await ctx.channel.send(f"<@{str(ctx.author.id)}>, you do not have proper permissions to use this command.")
            return
        sd_v = dfread("servers_dat")
        unset_cond = False
        if "auc" in sd_v[str(ctx.guild.id)]:
            if ctx.channel.id == sd_v[str(ctx.guild.id)]["auc"]:
                unset_cond = True
        if unset_cond:
            temp_doc = {"auc" : ctx.channel.id}
            serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$unset" : temp_doc})
            sd_v = dfread("servers_dat")
            sd_v[str(ctx.guild.id)].pop("auc")
            dfwrite("servers_dat",sd_v)
            await ctx.channel.send(f'<@{ctx.author.id}>, you have unset auction entry channel.')
            return
        temp_doc = {"auc" : ctx.channel.id}
        serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$set" : temp_doc})
        sd_v = dfread("servers_dat")
        sd_v[str(ctx.guild.id)]["auc"] = ctx.channel.id
        dfwrite("servers_dat",sd_v)
        embed = discord.Embed(colour = self.ecolor, description = f'Auction entry channel set to <#{str(ctx.channel.id)}> channel.')
        await ctx.channel.send(embed = embed)
    
    @commands.command(name="entry", aliases = ["auction-entry"])
    async def aucentry(self, ctx):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        sd_v = dfread("servers_dat")
        if "auc" not in sd_v[str(ctx.guild.id)]:
            await ctx.channel.send("Set auction entry channel first.")
            return
        if ctx.channel.id != sd_v[str(ctx.guild.id)]["auc"]:
            return
        questions=["**What do you want to auction ?**",
                   "**what must be the minimum starting bid ?**",
                   "**Preference like gems/ticks/usd/cards/dyes.**",
                   "**Image if any(attachment/link), else type `NO`**"]
        answers = []
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
            #await qmsg.delete()
            if i != 3:
                answers.append(str(message.content)[:25:])
            else:
                if message.attachments:
                    answers.append(message.attachments[0].url)
                else:
                    answers.append(str(message.content))
        embed = discord.Embed(color = self.ecolor, title="Auction Details", description=f"**Item** - {answers[0]}\n**Min. Bid** - {answers[1]}\n**Preference** - {answers[2]}")
        im_url = ""
        embed.set_footer(text = "By reacting, you agree to being DMed for auction status.\nReact with check to confirm auction details.")
        if answers[3].startswith("http") and answers[3].endswith(".png") or answers[3].endswith(".jpg"):
            embed.set_thumbnail(url = answers[3])
            im_url = answers[3]
        au_msg = await ctx.channel.send(ctx.author.mention, embed = embed)
        await au_msg.add_reaction("✅")
        def check_r(reaction,user):
            return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message.id == au_msg.id
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout = 25 ,check = check_r)
        except:
            embed = discord.Embed(color = 0xFF0000, title="Auction Details", description=f"**Item** - {answers[0]}\n**Min. Bid** - {answers[1]}\n**Preference** - {answers[2]}\n\n**Cancelled!**")
            if answers[3].startswith("http") and answers[3].endswith(".png") or answers[3].endswith(".jpg"):
                embed.set_thumbnail(url = answers[3])
            await au_msg.edit(embed = embed)
            return
        sd_v = dfread("servers_dat")
        if "auc_dt" not in sd_v[str(ctx.guild.id)]:
            sd_v[str(ctx.guild.id)]["auc_dt"] = []
            dfwrite("servers_dat",sd_v)
        for auc_lis in sd_v[str(ctx.guild.id)]["auc_dt"]:
            if ctx.author.id == auc_lis[0]:
                await ctx.channel.send(ctx.author.mention+", you already have a auction request in queue.")
                return
        if not (len(sd_v[str(ctx.guild.id)]["auc_dt"]) <= 20):
            await ctx.channel.send("Maximum number of requests reached. `i.e. 20`")
            return
        auc_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        embed = discord.Embed(color = 0x00FF00, title="Auction Details", description=f"**Item** - {answers[0]}\n**Min. Bid** - {answers[1]}\n**Preference** - {answers[2]}\n\n**Confirmed!**\nAuction code `{auc_code}`")
        if answers[3].startswith("http") and answers[3].endswith(".png") or answers[3].endswith(".jpg"):
            embed.set_thumbnail(url = answers[3])
        await au_msg.edit(embed = embed)
        answers[0][0].replace("☑", "").replace("·", "")
        sd_v = dfread("servers_dat")
        sd_v[str(ctx.guild.id)]["auc_dt"].append([ctx.author.id, auc_code, answers[0]+" · "+answers[1]+" · "+answers[2], im_url])
        dfwrite("servers_dat",sd_v)
        temp_doc = {"auc_dt" : sd_v[str(ctx.guild.id)]["auc_dt"]}
        serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$set" : temp_doc})
    
    @commands.command(name="auc-list", aliases = ["auction-list"])
    async def auction_ls(self, ctx, auc_id : str = None):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        sd_v = dfread("servers_dat")
        if "arole" not in sd_v[str(ctx.guild.id)]:
            await ctx.channel.send("Set Auction Manager role first. `m.auc-role <roleid>`")
            return
        if ctx.guild.get_role(sd_v[str(ctx.guild.id)]["arole"]) not in ctx.author.roles:
            return
        if "auc_dt" not in sd_v[str(ctx.guild.id)]:
            await ctx.channel.send("No auctions found in this server.")
            return
        auction_data = sd_v[str(ctx.guild.id)]["auc_dt"]
        auction_dict = {0 : "No auction request found."}
        page_c = 0
        for aulists in auction_data[::11]:
            page_c += 1
            au_dat = ""
            for au_list in auction_data[auction_data.index(aulists):auction_data.index(aulists)+11:]:
                au_dat += f"<@{au_list[0]}>\n`{au_list[1]}` · "+au_list[2]+"\n"
            auction_dict[page_c]=au_dat
        auc_msg = await ctx.channel.send(embed = discord.Embed(color = self.ecolor, title="Auction Requests", description=auction_dict[1 if page_c>0 else 0]))
        if page_c <= 1:
            return
        await auc_msg.add_reaction("◀️")
        await auc_msg.add_reaction("▶️")
        def check_reac(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"] and reaction.message.id == auc_msg.id
        cur_page = 1
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=25, check=check_reac)
                if str(reaction.emoji) == "▶️" and cur_page != page_c:
                    cur_page += 1
                    await auc_msg.edit(embed = discord.Embed(color = self.ecolor, title="Auction Requests", description=auction_dict[cur_page]))
                elif str(reaction.emoji) == "◀️" and cur_page > 1:
                    cur_page -= 1
                    await auc_msg.edit(embed = discord.Embed(color = self.ecolor, title="Auction Requests", description=auction_dict[cur_page]))
            except:
                break
        return
    @commands.command(name="auc", aliases = ["auction"])
    async def auction_sta(self, ctx, auc_id : str = None):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if auc_id == None:
            return
        sd_v = dfread("servers_dat")
        if "arole" not in sd_v[str(ctx.guild.id)]:
            await ctx.channel.send("Set Auction Manager role first. `m.auc-role <roleid>`")
            return
        if ctx.guild.get_role(sd_v[str(ctx.guild.id)]["arole"]) not in ctx.author.roles:
            return
        auction_data = sd_v[str(ctx.guild.id)]["auc_dt"]
        for auc_tion in auction_data:
            if auc_tion[1] == auc_id:
                embed = discord.Embed(color = self.ecolor, title="Auction Request", description=f"user : <@{auc_tion[0]}>\n\n `{auc_id}` · "+auc_tion[2])
                if auc_tion[3] != "":
                    embed.set_image(url = auc_tion[3])
                if auc_tion[2].startswith("☑"):
                    await ctx.channel.send(embed = embed)
                    await ctx.channel.send("Auction request is already approved.")
                    return
                embed.set_footer(text = "React with  ✅ to approve this auction.")
                cf_msg = await ctx.channel.send(embed = embed)
                await cf_msg.add_reaction("✅")
                await cf_msg.add_reaction("❌")
                def check_r(reaction,user):
                    return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == cf_msg.id
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout = 25 ,check = check_r)
                except:
                    return
                if str(reaction) == "✅":
                    color = 0x00FF00
                    title = "Auction Request Approved"
                    await cf_msg.edit(embed = discord.Embed(color = color, title="Auction Request", description=f"user : <@{auc_tion[0]}>\n\n `{auc_id}` · "+auc_tion[2]+"\nApproved"))
                    sd_v = dfread("servers_dat")
                    sd_v[str(ctx.guild.id)]["auc_dt"][auction_data.index(auc_tion)][2]="☑ "+sd_v[str(ctx.guild.id)]["auc_dt"][auction_data.index(auc_tion)][2]
                    dfwrite("servers_dat",sd_v)
                else:
                    color = 0xFF0000
                    title = "Auction Request Rejected"
                    await cf_msg.edit(embed = discord.Embed(color = color, title="Auction Request", description=f"user : <@{auc_tion[0]}>\n\n `{auc_id}` · "+auc_tion[2]+"\nRejected"))
                    sd_v = dfread("servers_dat")
                    sd_v[str(ctx.guild.id)]["auc_dt"].pop(auction_data.index(auc_tion))
                    dfwrite("servers_dat",sd_v)
                embed = discord.Embed(color = color, title = title, description=f"Server : {ctx.guild}\n`{auc_id}` · "+auc_tion[2])
                embed.set_footer(text = "For more contact your server admins.")
                try:
                    user = await ctx.guild.fetch_member(auc_tion[0])
                    await user.send(embed = embed)
                except:
                    try:
                        chnl = ctx.guild.get_channel(sd_v[str(ctx.guild.id)]["auc"])
                        await chnl.send(f"<@{auc_tion[0]}>", embed = embed)
                    except:
                        pass
                    pass
                sd_v = dfread("servers_dat")
                temp_doc = {"auc_dt" : sd_v[str(ctx.guild.id)]["auc_dt"]}
                serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$set" : temp_doc})
                return
        await ctx.channel.send("Auction request not found.")
        return
    
    @commands.command(name="auc-start", aliases = ["auction-start"])
    async def auction_start(self, ctx, auc_id : str = "",chnl : discord.TextChannel = None):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if auc_id == "" or len(auc_id) > 6:
            await ctx.channel.send("Auction request not found.")
            return
        if chnl == None:
            chnl = ctx.channel
        sd_v = dfread("servers_dat")
        if "arole" not in sd_v[str(ctx.guild.id)]:
            await ctx.channel.send("Set Auction Manager role first. `m.auc-role <roleid>`")
            return
        if ctx.guild.get_role(sd_v[str(ctx.guild.id)]["arole"]) not in ctx.author.roles:
            return
        auction_data = sd_v[str(ctx.guild.id)]["auc_dt"]
        for auc_tion in auction_data:
            if auc_tion[1] == auc_id:
                item, st_bid, pref = auc_tion[2].split(" · ")
                if item[0] != "☑":
                    cf_msg = await ctx.channel.send(embed = discord.Embed(color = self.ecolor, title="Start Auction", description="Auction is not approved! Do you still want to continue?"))
                    def check_r(reaction,user):
                        return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message.id == cf_msg.id
                    await cf_msg.add_reaction("✅")
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout = 25 ,check = check_r)
                    except:
                        return
                else:
                    item = item[1::]
                desc = f"Item : {item}\nMin. Bid : {st_bid}\nPreference : {pref}\n"
                desc += f"Auction id : `{auc_id}`\nUser : <@{auc_tion[0]}>"
                embed = discord.Embed(color = self.ecolor, title="Auction", description=desc)
                if auc_tion[3] != "":
                    embed.set_image(url = auc_tion[3])
                await chnl.send(embed=embed)
                sd_v = dfread("servers_dat")
                sd_v[str(ctx.guild.id)]["auc_dt"].pop(auction_data.index(auc_tion))
                dfwrite("servers_dat",sd_v)
                temp_doc = {"auc_dt" : sd_v[str(ctx.guild.id)]["auc_dt"]}
                serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$set" : temp_doc})
                return
        await ctx.channel.send("Auction request not found.")
    
    @commands.command(name = 'auc-role', aliases=["auction-role"])
    async def changearole(self, ctx, arole : discord.Role = None):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if arole == None:
            await ctx.channel.send("Invalid role.")
        if not(ctx.message.author.guild_permissions.administrator):
            await ctx.channel.send(f"<@{str(ctx.author.id)}>, you do not have proper permissions to use this command.")
            return
        temp_doc = {"arole" : arole.id}
        serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$set" : temp_doc})
        sd_v = dfread("servers_dat")
        sd_v[str(ctx.guild.id)]["arole"] = arole.id
        dfwrite("servers_dat",sd_v)
        embed = discord.Embed(colour = self.ecolor, description = f'Auction manager role set to :  <@&{arole.id}>')
        await ctx.channel.send(embed = embed)
        
def setup_auction(bot):
    bot.add_cog(auction(bot))