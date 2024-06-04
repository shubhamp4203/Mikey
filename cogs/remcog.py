import discord
import time
from discord.ext import commands
from discord.ext import tasks
from pymongo import MongoClient
import certifi
import asyncio

ca = certifi.where()
c_str = "mongodb+srv://nemesis:unUqvQGQbrSw3Ri8@cluster0.7auwy.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
serverdat_obj = MongoClient(c_str, tlsCAFile=ca).premiumd.premiums
serverdat_dict = {}
mods = [569168901204606996, 783317541799591977, 761923749179162675, 840224507036696616]
for post in serverdat_obj.find():
    serverdat_dict[post["_id"]] = post["premium"]
c_role = 882632099360821308 #875762631296843817 #date premium role id
m_role = c_role
guildid = 730011495685029949 #863010215045234688 #toman guild id

class Reminder(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command(name="premium")
    @commands.has_permissions(administrator=True)
    async def premium(self, ctx, memn : discord.Member, tim_e, ptype="c"):
        if ctx.author.bot:
            return
        if ctx.guild.id != guildid:
            return
        if ctx.author.id not in mods:
            return
        global serverdat_dict
        memn_id = memn.id
        memn = await ctx.guild.fetch_member(memn.id)
        try:
            tim_e = int(tim_e[:-1:])
            if not (ptype.lower().startswith("c") or ptype.lower().startswith("m")):
                x = 0/0
        except:
            await ctx.channel.send("Invalid subscription type or days provided.")
            return
        tim_s= 3600*24*tim_e
        if memn_id in serverdat_dict:
            serverdat_dict[memn_id][1] += round(tim_s)
            temp_doc = {"premium" : serverdat_dict[memn_id]}
            serverdat_obj.update_one({"_id" : memn_id}, {"$set" : temp_doc})
        else:
            serverdat_dict[memn_id] = [0 if ptype.lower().startswith("c") else 1 , round(tim_s+time.time())] #0 for clan 1 for mikey
            serverdat_obj.insert_one({"_id" : memn_id, "premium" : serverdat_dict[memn_id]})
        rid = c_role if ptype.lower().startswith("c") else m_role
        role = discord.utils.get(ctx.guild.roles, id = rid)
        if role not in memn.roles:
            await memn.add_roles(role)
        await ctx.channel.send(f"""{tim_e} days of **{role.name}** subscription added to <@!{memn_id}> user.""")
        
    @commands.command(name="balance", aliases = ["bal"])
    async def premiumg(self, ctx, memn : discord.Member = None):
        if ctx.guild.id != guildid:
            return
        memn = memn or ctx.author
        if memn.id != ctx.author.id and ctx.author.id not in mods:
            return
        if memn.id not in serverdat_dict:
            await ctx.channel.send(memn.mention+", you aren't subscribed to any premium yet.")
            return
        ptype = c_role if serverdat_dict[memn.id][0]==0 else m_role
        tl = (serverdat_dict[memn.id][1]-time.time())/(24*3600)
        tlstr = str(round(tl))+" days" if tl > 1 else str(round(tl*24))+" hours"
        embed = discord.Embed(color = 0x00FFB7, title = "Date Premium", description = f"Role : <@&{ptype}>\nTime left : {tlstr}")
        await ctx.channel.send(embed=embed)
    
    @commands.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def premiumreset(self, ctx, memn : discord.Member = None):
        if ctx.author.bot:
            return
        if not memn:
            return
        if ctx.author.id not in mods:
            return
        if ctx.guild.id != guildid:
            return
        global serverdat_dict
        if memn.id not in serverdat_dict.copy():
            return
        try:
            rid = c_role if serverdat_dict[memn.id][0] == 0 else m_role
            role = discord.utils.get(ctx.guild.roles, id = rid)
            memn = await ctx.guild.fetch_member(memn.id)
            if role in memn.roles:
                await memn.remove_roles(role)
        except Exception as e:
            raise e
            pass
        if memn.id in serverdat_dict:
            serverdat_dict.pop(memn.id)
            serverdat_obj.delete_one({"_id" : memn.id})
        await ctx.channel.send(f"Reset for `{memn.id}` was successfull.")
        
    @commands.command(name="premium-list")
    @commands.has_permissions(administrator=True)
    async def premiumlist(self, ctx):
        if ctx.author.bot:
            return
        if ctx.guild.id != guildid:
            return
        if ctx.author.id not in mods:
            return
        serverdat_dict1 = {}
        for post in serverdat_obj.find():
            serverdat_dict1[post["_id"]] = post["premium"][1]
        contents = []
        c = 0
        add_str = ""
        for userid in serverdat_dict1.keys():
            if c%10 == 0 and c != 0:
                contents.append(add_str)
                add_str = ""
            tl = (serverdat_dict1[userid]-time.time())/(24*3600)
            timel = str(round(tl))+" D" if tl > 1 else str(round(tl*24))+" H"
            add_str += f"<@!{userid}> • `{timel}`\n{userid}\n"
            if len(serverdat_dict1)-1 == c:
                contents.append(add_str)
            c +=1
        if len(contents)==0:
            contents.append("No premium member found")
        pages = len(contents)
        cur_page = 1
        message = await ctx.send(embed = discord.Embed(title = "Premium List", description = f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}"))
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                if str(reaction.emoji) == "▶️" and cur_page != pages:
                    cur_page += 1
                    await message.edit(embed = discord.Embed(title = "Premium List", description = f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}"))
                    await message.remove_reaction(reaction, user)
                elif str(reaction.emoji) == "◀️" and cur_page > 1:
                    cur_page -= 1
                    await message.edit(embed = discord.Embed(title = "Premium List", description = f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}"))
                    await message.remove_reaction(reaction, user)
                else:
                    await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                break
            
    @tasks.loop(minutes=1)
    async def check_rem(bot):
        global serverdat_dict
        for upre in serverdat_dict.copy():
            if serverdat_dict[upre][1]-time.time() < 0:
                guild = bot.get_guild(guildid)
                rid = c_role if serverdat_dict[upre][0] == 0 else m_role
                role = discord.utils.get(guild.roles, id = rid)
                try:
                    mem = await guild.fetch_member(upre)
                    serverdat_obj.delete_one({"_id" : upre})
                    serverdat_dict.pop(upre)
                    await mem.remove_roles(role)
                except Exception as e:
                    print(e)
                    continue
        return

def setup(bot):
    bot.add_cog(Reminder(bot))