from discord.ext import commands
import discord

class TopGG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_autopost_success(self):
        return
    
    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        'An event that is called whenever someone votes for the bot on Top.gg.'
        if data["type"] == "test":
            # this is roughly equivalent to
            # return await on_dbl_test(data) in this case
            return self.bot.dispatch('dbl_test', data)

        user = self.bot.get_user(data['user']) or await self.bot.fetch_user(data['user'])
        if user is None:
            return
        
        _type = f'Test Vote Recieved' if data['type'] == 'test' else f'{str(user)} just voted'
        embed = discord.Embed(title=_type, colour = 0x00FFB7, description = f"<@{user.id}> thank you for voting Mikey bot.\n[Click Here](https://top.gg/bot/861628000227164190/vote) **to vote mikey**")
        embed.set_thumbnail(url=user.display_avatar.url)
        channel = self.bot.get_channel(866923280316104705)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        'An event that is called whenever someone tests the webhook system for your bot on Top.gg.'
        print(f"Received a test vote:\n{data['user']}")

def setup(bot):
    bot.add_cog(TopGG(bot))