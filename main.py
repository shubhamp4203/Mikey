import discord
from discord.ext import commands, pages
import json
import os
from pymongo import MongoClient
import certifi
import json
from dotenv import load_dotenv
import colorama
from colorama import Fore
import datetime
import aiohttp
import asyncio
import aiosqlite
import asyncpg
from toppy.client import TopGG

from core import helper

import setproctitle


setproctitle.setproctitle("mikey-py")
load_dotenv()

colorama.init(autoreset=True)

def divide_chunks(l, n):
    return [l[i * n: (i + 1) * n] for i in range((len(l) + n - 1) // n)]

def botcolor(context):
    if isinstance(context, commands.Context):
        return context.guild.me.color if context.guild.me.color != discord.Color.default() else discord.Color.dark_red()
    elif isinstance(context, discord.Guild):
        return context.me.color if context.me.color != discord.Color.default() else discord.Color.dark_red()
    else:
        raise TypeError('Invalid context')

__cogs__ = [
    "effcalc",
    "error",
    "shardm",
    "e5",
    "framesuggestion",
    "giveaway",
    "vote_reminder",
    "info",
    "ed4codes",
    "wlLeaderboard",
    "misc",
    "vsbattle",
    "starboard",
    "vote_tracker"
]

plus_emj = "plus:863021349652004884"
mikey_emj = "<:mikeyy:866924000185286667>"
cancel_emj = "❌"

def get_command_signature(command):
    if command.parent != None:
        gname = f"{command.parent.qualified_name} {command.name}"
        return f"```\nm.{gname} {command.signature}\n```"
    return f"```\nm.{command.name} {command.signature}\n```"

def get_command_desc_only(command):
    if command.description != "":
        return f"```\n{command.description}\n```"
    else:
        return f"```\nNo Description Provided\n```"
    
def get_command_desc(command):
    if command.parent != None:
        gname = f"{command.parent.qualified_name} {command.name}"
        return f"```\nm.{gname} {command.signature}\n```"
    
    if command.description != "":
        return f"```\n{command.description}\n```"
    else:
        return f"```\nm.{command.name} {command.signature}\n```"



class HelpMenu(discord.ui.Select):
    def __init__(self, mapping, bot, ctx):
        self.bot = bot
        self.ctx = ctx
        self.mapping = mapping
        
        values = []
        integer = 0
        ignored_cogs = [ "Error", "Events", "TopGG", "Jishaku"]
        
        for cog_, cmds in self.mapping.items():
            if cog_:
                if cog_.qualified_name in ignored_cogs:
                    continue
            integer += 1
            if cog_ is None:
                values.append(discord.SelectOption(label=f"Extras", description="Mikey Extras", emoji=f'{mikey_emj}'))
            else:
                values.append(discord.SelectOption(label=f"{cog_.qualified_name}", description=cog_.description, emoji=f"{mikey_emj}"))
        values.append(discord.SelectOption(label='Close',
                                           description='Close the Help Menu.',
                                           emoji=cancel_emj))
        super().__init__(placeholder='Select a Command Category', min_values=1, max_values=1, options=values)
        
    async def callback(self, interaction: discord.Interaction):
        if str(self.values[0]) == 'Close':
            for item in self.view.children:
                if isinstance(item, discord.ui.Select):
                    item.placeholder = "Help Menu Closed."
                    item.disabled = True
            await interaction.message.edit(view=self.view)
            self.view.stop()
            return

        cog_ = self.ctx.bot.get_cog(self.values[0])

        pag = False

        if cog_ != None:
            cmds = cog_.get_commands()
            cmdsnew = []
            for command in cmds:
                if not isinstance(command, discord.ext.commands.Command):
                    continue
                if command.name == "help":
                    continue
                if command.hidden:
                    continue
                cmdsnew.append(command)
                    
            if len(cmdsnew) > 5:
                cog_name = cog_.qualified_name
                
                embeds = []

                chunks = divide_chunks(cmdsnew, 5)
                i = 1

                for chunk in list(chunks):
                    em = discord.Embed(title=f"{mikey_emj} {cog_name.upper()} COMMANDS", color=botcolor(self.ctx))
                    if cog_.description:
                        em.description = f"> {cog_.description}\n> Use `m.help [command]` for detailed info on a command"
                    em.set_image(url="https://media.discordapp.net/attachments/914774529425965156/914781181269123102/mikey_header_tokyo_revengers_by_xsava_deqlzyi-pre.jpg?width=1024&height=341")
                    for c in chunk:
                        em.add_field(name=c.name.upper(), value=get_command_desc(c), inline=False)
                    em.set_footer(text=f"Page {i}/{len(chunks)}", icon_url=self.ctx.bot.user.display_avatar.url)
                    embeds.append(em)
                    i += 1
                pag = True
            else:
                cog_name = cog_.qualified_name

                em = discord.Embed(title=f"{mikey_emj} {cog_name.upper()} COMMANDS", color=botcolor(self.ctx))

                if cog_.description:
                    em.description = f"> {cog_.description}"

                for command in cmds:
                    if command.name == "help":
                        continue
                    if not isinstance(command, discord.ext.commands.Command):
                        continue
                    if not command.hidden:
                        em.add_field(name=command.name.upper(), value=get_command_desc(command), inline=False)
                em.set_image(url="https://media.discordapp.net/attachments/914774529425965156/914781181269123102/mikey_header_tokyo_revengers_by_xsava_deqlzyi-pre.jpg?width=1024&height=341")
                em.set_footer(text="Use m.help [command] for detailed info on a command", icon_url=self.ctx.bot.user.display_avatar.url)
        else:
            em = discord.Embed(title=f"{mikey_emj} EXTRA COMMANDS", color=botcolor(self.ctx))
            em.description = f"> Mikey Extras"
            for command in self.ctx.bot.commands:
                if command.name == "help":
                    continue
                if not isinstance(command, discord.ext.commands.Command):
                    continue
                if command.cog == None:
                    if not isinstance(command, discord.commands.SlashCommand):
                        if not command.hidden:
                            em.add_field(name=command.name.upper(), value=get_command_desc(command), inline=False)
            if len(em.fields) == 0:
                em.description = f"Mikey Extras\n> ```\n> There aren't any command registered under this command category.\n> ```"
            em.set_image(url="https://media.discordapp.net/attachments/914774529425965156/914781181269123102/mikey_header_tokyo_revengers_by_xsava_deqlzyi-pre.jpg?width=1024&height=341")
            em.set_footer(text="Use m.help [command] for detailed info on a command", icon_url=self.ctx.bot.user.display_avatar.url)

        if pag:
            # paginator = DiscordUtils.Pagination.CustomEmbedPaginator(self.ctx, timeout=300, remove_reactions=True)
            # paginator.add_reaction(
            # "⏮️", "first"
            # )
            # paginator.add_reaction(
            # "⏪", "back")
            # paginator.add_reaction(
            # "⏩", "next")
            # paginator.add_reaction(
            # "⏭️", "last"
            # )
            # await interaction.response.defer(ephemeral=False)
            # await paginator.run(embeds)
            # page_buttons = [
            #     pages.PaginatorButton(
            #         "first", emoji="⏮️", style=discord.ButtonStyle.gray
            #     ),
            #     pages.PaginatorButton("prev", emoji="⏪", style=discord.ButtonStyle.gray),
            #     pages.PaginatorButton(
            #         "page_indicator", style=discord.ButtonStyle.blurple, disabled=True
            #     ),
            #     pages.PaginatorButton("next", emoji="⏩", style=discord.ButtonStyle.gray),
            #     pages.PaginatorButton("last", emoji="⏭️", style=discord.ButtonStyle.gray),
            # ]
            
            paginator = pages.Paginator(pages=embeds, show_indicator=True, loop_pages=True, author_check=True, disable_on_timeout=True, show_disabled=True, timeout=300.0)
            await paginator.respond(interaction, ephemeral=False)
        else:
            await interaction.response.send_message(embed=em)



class HelpMenuView(discord.ui.View):
    def __init__(self, mapping, bot, ctx):
        super().__init__(timeout=300.0)
        self.ctx = ctx
        self.bot = bot
        self.add_item(HelpMenu(mapping, bot, ctx))
	
    async def on_error(self, error, item, interaction):
        pass
    
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("You are not authorized to use the Help Menu!", ephemeral=True)
            return False
        else:
            return True
        
    async def on_timeout(self):
        try:
            for item in self.children:
                if isinstance(item, discord.ui.Select):
                    item.placeholder = "Options disabled due to timeout."
                    item.disabled = True
            await self.message.edit(view=self)
        except:
            pass



class HelpCommand(commands.HelpCommand):
    async def send_error_message(self, error):
        embed = discord.Embed(title= f"NO SUCH COMMAND FOUND", description= f"Join our **[SUPPORT SERVER](https://discord.gg/dWttazRJ5f)** for any kind of help. Use the following command to know more:```\nm.help\n```", colour = 0xff0000)
        embed.set_footer(icon_url = self.context.author.display_avatar.url)
        embed.set_thumbnail(url = self.context.bot.user.display_avatar.url)
        await self.context.reply(embed=embed)
    
    def command_not_found(self, string):
        return "**No such command found. Use `m.help` to know more!**"
    
    def get_command_signature(self, command):
        if isinstance(command, discord.commands.SlashCommand):
            return
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = '|'.join(command.aliases)
            fmt = f'[{command.name}|{aliases}]'
            if parent:
                fmt = f'{parent}, {fmt}'
            alias = fmt
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {command.signature}'

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title=f'{mikey_emj}MIKEY HELP')
        description = self.context.bot.description
        if description:
            embed.description = f"{description}"

        embed.set_footer(text="Use m.help [command] for detailed info on a command", icon_url=self.context.bot.user.display_avatar.url)
        embed.color = botcolor(self.context)
        embed.set_image(url="https://media.discordapp.net/attachments/914774529425965156/914781181269123102/mikey_header_tokyo_revengers_by_xsava_deqlzyi-pre.jpg?width=1024&height=341")
        
        hview = HelpMenuView(mapping, self.context.bot, self.context)
        hview.add_item(discord.ui.Button(label='Support Server', url='https://discord.gg/dWttazRJ5f', style=discord.ButtonStyle.url))
        hview.add_item(discord.ui.Button(label='Invite', url='https://discord.com/oauth2/authorize?client_id=861628000227164190&permissions=388192&scope=bot', style=discord.ButtonStyle.url))
        hview.message = await self.context.reply(embed=embed, view=hview, mention_author=False)

    async def send_cog_help(self, cog_):
        embed = discord.Embed(title= f"NO SUCH COMMAND FOUND", description= f"Join our **[SUPPORT SERVER](https://discord.gg/dWttazRJ5f)** for any kind of help. Use the following command to know more:```\nm.help\n```", colour = 0xff0000)
        embed.set_footer(icon_url = self.context.author.display_avatar.url)
        embed.set_thumbnail(url = self.context.bot.user.display_avatar.url)
        await self.context.reply(embed=embed)
        

    async def send_group_help(self, group):
        embed = discord.Embed(title=f"{mikey_emj} {group.qualified_name.upper()} CATEGORY HELP")
        embed.set_footer(text="<> Denotes required argument. [] Denotes optional argument", icon_url=self.context.bot.user.display_avatar.url)
        embed.color = botcolor(self.context)
        embed.set_thumbnail(url = self.context.bot.user.display_avatar.url)
        
        embed.description = "> Use `m.help` to know more about all the commands"
        
        if isinstance(group, commands.Group):
            for command in group.commands:
                if command.name == "help":
                    continue
                if isinstance(command, commands.Command):
                    if not command.hidden:
                        gname = f"{group.qualified_name} {command.name}"
                        embed.add_field(name=gname.capitalize(), value=get_command_desc(command), inline=False)

        embed.set_footer(text="<> Denotes required argument. [] Denotes optional argument", icon_url=self.context.bot.user.display_avatar.url)
        await self.context.reply(embed=embed, mention_author=False)

    async def send_command_help(self, command):
        if not isinstance(command, discord.ext.commands.Command):
            return
        if command.parent:
            gname = f"{command.parent.qualified_name} {command.name}"
            embed = discord.Embed(title=f"{mikey_emj} {gname.upper()} COMMAND HELP")
        else:
            embed = discord.Embed(title=f"{mikey_emj} {command.name.upper()} COMMAND HELP")
        embed.set_footer(text="<> Denotes required argument. [] Denotes optional argument", icon_url=self.context.bot.user.display_avatar.url)
        embed.color = botcolor(self.context)

        embed.set_thumbnail(url = self.context.bot.user.display_avatar.url)
        
        embed.description = "> Use `m.help` to know more about all the commands"
        
        if isinstance(command, discord.ext.commands.Command):
            if not command.hidden:
                embed.add_field(name="Usage:", value=get_command_signature(command), inline=False)
                embed.add_field(name="Description:", value=get_command_desc_only(command), inline=False)
                if command.cog:
                    embed.add_field(name="Command Category:", value=f"```\n{command.cog.qualified_name}\n```", inline=False)
                else:
                    embed.add_field(name="Command Category:", value=f"```\Extras\n```", inline=False)
                if command.aliases != []:
                    al = " | ".join(x for x in command.aliases)
                    embed.add_field(name="Aliases:", value=f"```\n{al}\n```", inline=False)
                else:
                    embed.add_field(name="Aliases:", value=f"```\nNone\n```", inline=False)
            else:
                return await self.context.reply("You are not authorized to view the command!")
        
        embed.set_footer(text="<> Denotes required argument. [] Denotes optional argument", icon_url=self.context.bot.user.display_avatar.url)
        await self.context.reply(embed=embed)




async def create_db_pool():
    return await asyncpg.create_pool(database="railway", user="postgres", host="containers-us-west-17.railway.app", port=7620, password="3YWbACFbCPB2iyNuNGLM")

class MikeyBot(commands.AutoShardedBot):
    async def evalsql(self, database, sql, vals:tuple=(), fetch=None):
        conn = await aiosqlite.connect(database, timeout=25)
        conn.row_factory = self._dict_factory
        cursor = await conn.cursor()
        cursor = await cursor.execute(sql, vals)

        data = None # avoid UnboundLocalError
        if fetch == 'one':
            data = await cursor.fetchone()
        elif fetch == 'all':
            data = await cursor.fetchall()
        
        if fetch:
            pass
        else:
            await conn.commit()
        
        await cursor.close()
        await conn.close()
        return data

    def _dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    async def not_blacklisted(self, ctx):
        await self.evalsql(database='./Database/blacklist.db', sql='CREATE TABLE IF NOT EXISTS users (user_id INT, banned_on TEXT, reason TEXT)')
        user_id = await self.evalsql(database='./Database/blacklist.db', sql='SELECT * FROM users WHERE user_id=?', vals=(int(ctx.author.id),), fetch='one')
        if not user_id:
            return True
        else:
            raise helper.UserBlacklisted(f"{ctx.author} is blacklisted for using the bot!")
    
    async def get_prefix(self, message: discord.Message):
        prefixlist = ["m.", "M."]
        if not message.guild:
            return commands.when_mentioned_or(*prefixlist)(self, message)
        if self.server_prefix.get(message.guild.id):
            g_pre = self.server_prefix[message.guild.id]
            if g_pre == "m.":
                return commands.when_mentioned_or(*prefixlist)(self, message)
            return commands.when_mentioned_or(g_pre)(self, message)
        else:
            g_pre = "m."
            temp_doc = {"prefix" : g_pre}
            try:
                self.serverdat_obj.update_one({"_id" : message.guild.id}, {"$set" : temp_doc})
            except:
                self.serverdat_obj.insert_one({"_id" : message.guild.id, "prefix" : "m."})
            sd_v = self.dfread("servers_dat")
            if (sd_v.get(str(message.guild.id)) == None) or (sd_v[str(message.guild.id)].get("prefix") == None):
                try:
                    sd_v[str(message.guild.id)]["prefix"] = "m."
                except:
                    sd_v[str(message.guild.id)]={"prefix":"m."}
                self.dfwrite("servers_dat",sd_v)
            self.server_prefix[message.guild.id] = g_pre
            if g_pre == "m.":
                return commands.when_mentioned_or(*prefixlist)(self, message)
            return commands.when_mentioned_or(g_pre)(self, message)

    async def ch_pr(self):
        await self.wait_until_ready()
        while not self.is_closed():
            if self.status_counter < 1:
                self.stat = f"m.help in {len(self.guilds)} servers!"
            try:
                bstat = self.stat.format(cards = self.card_count)
            except KeyError:
                bstat = self.stat.format(stats = len(self.guilds))
            except:
                bstat = self.stat
            await self.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name=bstat))
            self.status_counter += 1
            await asyncio.sleep(15)
        
        
    def dfread(self, df_type):
        with open(f'./{df_type}.json', 'r') as sd :
            sd_v = json.load(sd)
        return sd_v

    def dfwrite(self, df_type,dat):
        with open(f'./{df_type}.json', 'w') as sd :
            json.dump(dat, sd)

    def dfcheck(self, guild_id,sd_v):
        if guild_id not in sd_v.keys():
            return False
        else:
            return True

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=["m.", "M."],
            case_insensitive=True,
            strip_after_prefix=True,
            description="> Become a member of **[Mikey's Patreon](https://www.patreon.com/Mikeybot)** to experience premium exclusive features. Join our **[SUPPORT SERVER](https://discord.gg/dWttazRJ5f)** if you find any bugs/willing to suggest any features. \n```\nInvite me by using m.invite command.\n```",
            help_command=HelpCommand(),
            chunk_guilds_at_startup=False,
            intents=intents
        )
        ''' intents = discord.Intents(
                bans=True, 
                dm_messages=True,
                emojis=True,
                emojis_and_stickers=True,
                guild_messages=True,
                guild_reactions=True,
                guilds=True,
                messages=True,
                reactions=True
        )'''
        self.status_counter = 0
        self.owner_ids = [569168901204606996, 701284844600295466, 840224507036696616, 843400308008812545]
        self.session : aiohttp.ClientSession = None
        
        # self.pg_con: asyncpg.Pool = self.loop.run_until_complete(create_db_pool())
        self.c_str = os.getenv("CONNECTION_STRING")
        ca = certifi.where()
        self.serverdat_obj = MongoClient(self.c_str, tlsCAFile=ca).mickeydb.serverdat
        
        print(Fore.GREEN + "Connected to database")
        print(Fore.RED + "--------------------------")
        
        
        self.serverdat_dict = {}
        self.server_prefix = {}
        self.eff_channels = {}
        
        self.debug = False
        self.version = "v3.0"
        self.allowed_mentions = discord.AllowedMentions(replied_user=False)
        
        self.add_check(self.not_blacklisted)
        self.loop.create_task(self.ch_pr())
        self.loop.run_until_complete(self.postdb())
        
        print(Fore.YELLOW + "Updated Guild Caches")
        print(Fore.RED + "--------------------------")
        
        for cogname in __cogs__:
            self.load_my_extension("cogs." + cogname)

        self.load_my_extension("jishaku")
        print(Fore.CYAN + "Loaded Cogs")
        print(Fore.RED + "--------------------------")
        
        self.ecolor = 0x00FFB7

        dbltoken = os.getenv("DBL_TOKEN")
        self.top_gg = TopGG(self, token=dbltoken, autopost=True)
        
        
        
    def load_my_extension(self, name: str):
        try:
            self.load_extension(name)
        except Exception as e:
            print(e)

    async def on_ready(self):
        await asyncio.sleep(0.1)
        self.load_my_extension("cogs.events")
        print(Fore.MAGENTA + f"{self.user} is Online")
        print(Fore.RED + "--------------------------")
        
        self.uptime = datetime.datetime.utcnow()
        # channel = self.get_channel(870275991883358278)
        # if channel:
        #     await channel.send("<:tga_76:897848730923991050> Online aa gaya mein bc!")

    async def postdb(self):
        for post in self.serverdat_obj.find():
            self.serverdat_dict[post["_id"]] = post
            self.server_prefix[int(post["_id"])] = post["prefix"]
            if "autoec" in post:
                self.eff_channels[int(post["_id"])] = post["autoec"]
        self.dfwrite("servers_dat", self.serverdat_dict)

bot_token = os.getenv("BOT_TOKEN")
bot = MikeyBot()

bot.run(bot_token, reconnect=True)
