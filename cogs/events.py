from discord.ext import commands
import discord

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.last_time = time()
        # self.bot.solved_count = 0
    
    """@commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id not in [893408366032977940, 893408298840256552, 874183195409674290, 895205538420391946, 895205212258701322, 895280243156320256, 895280243156320256, 868483262694178836, 895904940785012786, 895904581979103253, 868610122711199774, 868610074304708710, 894832773821517874, 894832758587817984, 896035140034252871, 896035042772533288]:
            return
        if message.author.id != 861628000227164190:
            return
        if not message.embeds:
            return
        if "Solution" not in message.embeds[0].title:
            return
        counter = message.embeds[0].title
        if time() - self.last_time > 24*3600:
            self.bot.solved_count = 0
        if counter == "Solution":
            self.bot.solved_count += 1"""
            
                
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != 646937666251915264:
            return
        if "A card from your wishlist is dropping!" not in message.content:
            return
        sd_v = self.bot.dfread("servers_dat")
        if "wlrole" not in sd_v[str(message.guild.id)]:
            return
        wishlist_ping = f"A wishlisted card is dropping <@&{sd_v[str(message.guild.id)]['wlrole']}>"
        await message.reply(wishlist_ping)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        ch = self.bot.get_channel(936273591266336871)
        embed = discord.Embed(title='JOINED GUILD', color=discord.Color.gold())
        try:
            embed.set_thumbnail(url=guild.icon.url)
        except:
            pass
        embed.add_field(name='NAME', value=guild.name, inline=True)
        embed.add_field(name='GUILD ID', value=guild.id, inline=True)
        if guild.owner_id:
            server_owner = await self.bot.fetch_user(guild.owner_id)
            embed.add_field(name='OWNER', value=f'{server_owner}', inline=True)
            embed.add_field(name='OWNER ID', value=f'{guild.owner_id}', inline=True)
        embed.add_field(name='CHANNELS', value=len(guild.channels), inline=True)
        embed.add_field(name='MEMBER COUNT', value=guild.member_count, inline=True)
        embed.add_field(name='GUILD CREATED AT', value=guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=True)
        await ch.send(embed = embed)
        
        try:
            self.bot.serverdat_obj.insert_one({"_id" : guild.id, "prefix" : "m."})
            sd_v = self.bot.dfread("servers_dat")
            sd_v[str(guild.id)] = {"_id" : guild.id, "prefix" : "m."}
            self.bot.dfwrite("servers_dat",sd_v)
            self.bot.server_prefix[guild.id] = "m."
        except:
            return
        
        
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        ch = self.bot.get_channel(936273626674630696)
        embed = discord.Embed(title='LEFT GUILD', color=0xff0000)
        try:
            embed.set_thumbnail(url=guild.icon.url)
        except:
            pass
        embed.add_field(name='NAME', value=guild.name, inline=True)
        embed.add_field(name='GUILD ID', value=guild.id, inline=True)
        if guild.owner_id:
            server_owner = await self.bot.fetch_user(guild.owner_id)
            embed.add_field(name='OWNER', value=f'{server_owner}', inline=True)
            embed.add_field(name='OWNER ID', value=f'{guild.owner_id}', inline=True)
        embed.add_field(name='CHANNELS', value=len(guild.channels), inline=True)
        embed.add_field(name='MEMBER COUNT', value=guild.member_count, inline=True)
        embed.add_field(name='GUILD CREATED AT', value=guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=True)
        await ch.send(embed = embed)
        
        try:
            self.bot.serverdat_obj.delete_one({"_id" : guild.id})
            sd_v = self.bot.dfread("servers_dat")
            sd_v.pop(str(guild.id))
            self.bot.dfwrite("servers_dat",sd_v)
            self.bot.server_prefix.pop(guild.id)
        except:
            return
    
def setup(bot):
    bot.add_cog(Events(bot))
