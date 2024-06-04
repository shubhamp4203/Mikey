import discord
from discord.ext import commands
import json
import asyncio

with open("votingdata.json", "r") as f1:
    voting_data = json.load(f1)


class voterem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="remindme", aliases=['rm'])
    async def voteremind(self, ctx, thing=None):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if thing == None:
            await ctx.reply("Please mention what I should remind you for.")
            return
        if not thing.lower() == "vote":
            await ctx.reply("Sorry I cannot remind for that thing.")
            return
        if str(ctx.author.id) not in voting_data.keys():
            for i in voting_data.keys():
                print(type(i))
            voting_data[str(ctx.author.id)] = True
            await ctx.reply("Alright I will Dm you to remind for voting mikey.")
            with open("votingdata.json", "w") as f1:
                json.dump(voting_data, f1, indent=4)
            return
        if voting_data[str(ctx.author.id)] == True:
            voting_data[str(ctx.author.id)] = False
            await ctx.reply("Voting reminder is now disabled.")
            with open("votingdata.json", "w") as f1:
                json.dump(voting_data, f1, indent=4)
            return
        if voting_data[str(ctx.author.id)] == False:
            voting_data[str(ctx.author.id)] = True
            await ctx.reply("Voting reminder is now enabled.")
            with open("votingdata.json", "w") as f1:
                json.dump(voting_data, f1, indent=4)
            return

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id != 943541008220713030:
            return
        if msg.channel.id != 866923280316104705:
            return
        if not msg.embeds:
            return
        user_id = msg.embeds[0].description.split("\n")[0].split(" ")[0].replace("<@", "").replace(">", "")
        if user_id not in voting_data.keys():
            return
        if not voting_data[user_id] == True:
            return
        user = await self.bot.fetch_user(user_id)
        await asyncio.sleep(43210)
        await user.send("Hey! You can now vote for Mikey Bot.\nhttps://top.gg/bot/861628000227164190/vote")
def setup(bot):
    bot.add_cog(voterem(bot))
