import discord
from discord.ext import commands
import json

def getchnl(guildid):
    with open("servers_dat.json", "r") as fi:
        sd_v = json.load(fi)
    if not sd_v.get(str(guildid)): return None
    return sd_v[str(guildid)]["starb"]

def star_coun(guildid):
    with open("servers_dat.json", "r") as fi:
        sd_v = json.load(fi)
    if not sd_v.get(str(guildid)): return None
    if "starc" in sd_v[str(guildid)]:
        return sd_v[str(guildid)]["starc"]
    else:
        return 3

class Starboard(commands.Cog):
    """
    Your message goes to the starboard if its star reaction crosses a certain threshold.
    """
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            reguild = self.bot.get_guild(payload.guild_id)
            reactchannel = reguild.get_channel(payload.channel_id)
            message = await reactchannel.fetch_message(payload.message_id)
        except:
            return
        if reactchannel == None or message == None:
            return
        
        match = False
        
        obj = self.bot.dfread("reactions")
        list = obj["reacted"]
        if list != []:
            if str(message.id) in list:
                match = True
       
        if match:
            return
        isstar = False
        star_c = star_coun(payload.guild_id)
        if not star_c: return
        for i in message.reactions:
            if i.emoji == ("⭐") and i.count >= star_c:
                isstar = True
        if not isstar:
            return
        try:
            if not getchnl(payload.guild_id): return
            board = message.guild.get_channel_or_thread(getchnl(payload.guild_id))
            if not board: 
                return await message.reply("Starboard channel not found")
        except:
            return
        embed = discord.Embed(colour = self.bot.ecolor, description = f"In {reactchannel.mention}. [Link to the message]({message.jump_url})")
        embed.set_author(name = message.author.name, icon_url = message.author.display_avatar.url)
        embed.add_field(name = "Message", value = message.content, inline = False)
        try:
            if message.content.startswith('https://'):
                embed.set_image(url=message.content)
        except:
            pass
        try:
            attach = message.attachments
            embed.set_image(url = attach[0].url)
        except:
            pass
        # sending actual embed
        await board.send(embed=embed)
        obj["reacted"].append(str(message.id))
        self.bot.dfwrite("reactions", obj)
    
    @commands.command(name="star")
    @commands.has_permissions(administrator=True)
    async def star_it(self, ctx):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if not ctx.message.reference:
            return
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        reactchannel = ctx.channel
        try:
            if not getchnl(ctx.guild_id): return
            board = message.guild.get_channel(getchnl(ctx.guild.id))
            if not board: 
                return await ctx.reply("Starboard channel not found")
        except:
            return
        await message.add_reaction("⭐")
        embed = discord.Embed(colour = self.bot.ecolor, description = f"In {reactchannel.mention}. [Link to the message]({message.jump_url})")
        embed.set_author(name = message.author.name, icon_url = message.author.display_avatar.url)
        embed.add_field(name = "Message", value = message.content, inline = False)
        try:
            if message.content.startswith('https://'):
                embed.set_image(url=message.content)
        except:
            pass
        try:
            attach = message.attachments
            embed.set_image(url = attach[0].url)
        except:
            pass
        # sending actual embed
        await board.send(embed = embed)
        obj = self.bot.dfread("reactions")
        obj["reactions"].append(str(message.id))
        self.bot.dfwrite("reacted", obj)
        
        
    @commands.command(name = 'set-starb', aliases = ["set-starboard"])
    async def setstarb(self, ctx, s_count : int = 3):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if not ctx.message.author.guild_permissions.administrator:
            await ctx.channel.send(f"<@{str(ctx.author.id)}>, you do not have proper permissions to use this command.")
            return
        if s_count < 1:
            s_count = 1
        sd_v = self.bot.dfread("servers_dat")
        unset_cond = False
        if "starb" in sd_v[str(ctx.guild.id)]:
            if ctx.channel.id == sd_v[str(ctx.guild.id)]["starb"]:
                unset_cond = True
        if unset_cond:
            temp_doc = {"starb" : ctx.channel.id}
            if "starc" in sd_v[str(ctx.guild.id)]:
                temp_doc1 = {"starc" : 1}
                self.bot.serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$unset" : temp_doc1})
                sd_v[str(ctx.guild.id)].pop("starc")
            self.bot.serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$unset" : temp_doc})
            sd_v[str(ctx.guild.id)].pop("starb")
            self.bot.dfwrite("servers_dat",sd_v)
            await ctx.reply(f'<@{ctx.author.id}>, you have unset starboard channel.')
            return
        temp_doc = {"starb" : ctx.channel.id}
        temp_doc1 = {"starc" : s_count}
        self.bot.serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$set" : temp_doc1})
        self.bot.serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$set" : temp_doc})
        sd_v[str(ctx.guild.id)]["starb"] = ctx.channel.id
        sd_v[str(ctx.guild.id)]["starc"] = s_count
        self.bot.dfwrite("servers_dat",sd_v)
        embed = discord.Embed(colour = 0x00FFFF, description = f'Starboard channel set to <#{str(ctx.channel.id)}> channel with minimum `{s_count}` star reactions to trigger.')
        await ctx.reply(embed = embed)

def setup(bot):
    bot.add_cog(Starboard(bot))
