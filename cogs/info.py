import discord
from discord.ext import commands
from discord import slash_command
import humanize, datetime
import psutil
import time

class Info(commands.Cog):
    """
    Commands related to Mikey Bot.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.ecolor =0x00FFB7
    '''
    @commands.slash_command(name = "ping")
    async def ping(self, ctx):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        async with ctx.channel.typing():
            embed = discord.Embed(title="🏓 PONG!", description=f'Ping:  `{round(self.bot.latency * 1000)}ms`', color = discord.Color.blue())
            await ctx.respond(embed=embed)'''

    @slash_command(name = "ping", description = "Bot latency.")
    async def ping_c(self, itx):
        await itx.response.send_message(embed = discord.Embed(title="🏓 PONG!", description=f'Ping:  `{round(self.bot.latency * 1000)}ms`', color = discord.Color.blue()))
        return
    @commands.command(name = "support", aliases = ["server"])
    async def supportl(self, ctx):
        if ctx.author.bot:
            return
        embed = discord.Embed(colour = self.ecolor, title = "Mikey❦#6287 Bot Support Server", description = "[Click Here](https://discord.gg/dWttazRJ5f) to join Mikey bot's support server.")
        
        hview = discord.ui.View()
        hview.add_item(discord.ui.Button(label='Support Server', url='https://discord.gg/dWttazRJ5f', style=discord.ButtonStyle.url))
        hview.add_item(discord.ui.Button(label='Invite', url='https://discord.com/oauth2/authorize?client_id=861628000227164190&permissions=388192&scope=bot', style=discord.ButtonStyle.url))
        
        await ctx.channel.send(embed = embed, view=hview)
    
    @commands.command(name = "invite")
    async def invitel(self, ctx):
        if ctx.author.bot:
            return
        bot_av = self.bot.user.display_avatar.url
        embed = discord.Embed(colour = self.ecolor, title = "Mikey❦#6287 Discord Bot", description = "[Click Here](https://discord.com/oauth2/authorize?client_id=861628000227164190&permissions=388192&scope=bot) to add Mikey bot to your server.")
        embed.set_thumbnail(url = bot_av)
        await ctx.channel.send(embed = embed)

    @commands.command(name = "vote")
    async def votel(self, ctx):
        if ctx.author.bot:
            return
        bot_av = self.bot.user.display_avatar.url
        hview = discord.ui.View()
        hview.add_item(discord.ui.Button(label='Vote', url='https://top.gg/bot/861628000227164190/vote', style=discord.ButtonStyle.url))
        
        embed = discord.Embed(colour = self.ecolor, title = "Vote Mikey❦#6287", description = "[Click Here](https://top.gg/bot/861628000227164190/vote) to vote me.")
        embed.set_thumbnail(url = bot_av)
        await ctx.channel.send(embed = embed, view=hview)
        
    @commands.command(name = "ping", aliases = ["latency"])
    async def ping(self, ctx):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        async with ctx.channel.typing():
            embed = discord.Embed(title="🏓 PONG!", description=f'Ping: `{round(self.bot.latency*1000)}ms`', color=discord.Color.blue())
            await ctx.send(embed=embed)

    
    @commands.command(name = "stats", aliases=["botinfo"])
    async def guilds_info(self, ctx):
        delta = datetime.datetime.utcnow() - self.bot.uptime
        total_m = 0
        total_g = 0
        for guild in self.bot.guilds:
            total_g += 1
            total_m += guild.member_count
            
        embed=discord.Embed(title=f"{self.bot.user.name} Bot Statistics", colour = self.ecolor)
        
        embed.add_field(name="Bot Developers", value="INFINIX#7276, SuniL#4342, ClawX69#9782", inline=True)
        embed.add_field(name="Total Servers", value=str(total_g), inline=True)
        embed.add_field(name="Total Members", value=str(total_m), inline=True)
        
        embed.add_field(name="Ping", value=f"{round(self.bot.latency*1000)}ms", inline=True)
        embed.add_field(name="Bot Uptime", value=f"{humanize.precisedelta(delta)}", inline=True)
        embed.add_field(name="Bot Version", value=f"{self.bot.version}", inline=True)
        
        embed.add_field(name = 'CPU Usage', value = f'{round(psutil.cpu_percent())}%', inline = True)
        embed.add_field(name = 'Memory Usage', value = f'{round(psutil.virtual_memory().percent)}%', inline = True)
        embed.add_field(name = 'Available Memory', value = f'{round(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)}%', inline = True)
        
        embed.set_footer(text=f"Bot ID: {self.bot.user.id}")
        embed.set_thumbnail(url = self.bot.user.avatar.url)
        await ctx.reply(embed = embed)
        
def setup(bot):
    bot.add_cog(Info(bot))
