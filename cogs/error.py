from discord.ext import commands
from core import helper
import discord

class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(f"That user could not be found!")
            return
        elif isinstance(error, commands.NotOwner):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have proper permissions to use this command.")
            return
        elif isinstance(error, commands.BadArgument):
            if ctx.command.parent:
                params = f"m.{ctx.command.parent.qualified_name} {ctx.command.name} {ctx.command.signature}"
            else:
                params = f"m.{ctx.command.name} {ctx.command.signature}"
            await ctx.send(f"Invalid input. Please use the command like this:\n```{params}```")
            return
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have sufficient permissions!")
            return
        elif isinstance(error,commands.MissingRequiredArgument):
            if ctx.command.parent:
                params = f"m.{ctx.command.parent.qualified_name} {ctx.command.name} {ctx.command.signature}"
            else:
                params = f"m.{ctx.command.name} {ctx.command.signature}"
            await ctx.send(f"Please use the command like this:\n```{params}```")
        elif isinstance(error, commands.errors.BadArgument):
            if ctx.command.parent:
                params = f"m.{ctx.command.parent.qualified_name} {ctx.command.name} {ctx.command.signature}"
            else:
                params = f"m.{ctx.command.name} {ctx.command.signature}"
            await ctx.send(f"Invalid input. Please use the command like this:\n```{params}```")
            return
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"<@{ctx.author.id}>, slow it down! Try again in `{error.retry_after:.2f}s`.")
            return
        elif isinstance(error, helper.UserBlacklisted):
            blackuser = await self.bot.evalsql(database='./Database/blacklist.db', sql='SELECT * FROM users WHERE user_id=?', vals=(ctx.author.id,), fetch='one')

            embed = discord.Embed(title= f"YOU ARE BANNED FROM USING {self.bot.user.name}", description= f"Uh-oh! You are banned from using me. You can't use any of my commands now!", colour = 0xff0000)
            embed.add_field(name="Reason", value=blackuser['reason'])
            embed.set_footer(icon_url = ctx.author.display_avatar.url)
            embed.set_thumbnail(url = self.bot.user.display_avatar.url)
            #await ctx.reply(embed = embed)
        else:
            await ctx.reply("Error Occured.")
            return
            '''
            if hasattr(error, 'original'):
                await ctx.reply(f"```\n{error.original}\n```")
            else:
                await ctx.reply(f"```\n{error}\n```")
            '''
    
def setup(bot):
    bot.add_cog(Error(bot))
