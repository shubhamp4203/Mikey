import discord
from discord.ext import commands
import os
import json

cond_list = ["☆☆☆☆", "★☆☆☆", "★★☆☆", "★★★☆", "★★★★"]
def condup(curr_eff,curr_cond):
    mint_eff = curr_eff
    curr_cond += 1
    for _ in range(curr_cond,5):
        mint_eff += ((mint_eff/100)*89)
    return round(mint_eff)

def basecal(base_val,cond):
    cond += 1
    for _ in range(cond,5):
        base_val *= 2
    return base_val

def closest(lst, K):
    return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]

def autoeff(cond,desc,sty_l = 0):
    desc = desc.split("\n\n")
    final_txt = ""
    final_txt += desc[0].split("\n")[0] + "\n\n"
    curr_eff = int(desc[0].split("\n")[1].split("**")[1])
    if desc[1].startswith("`Injured`"):
        final_txt += f"Effort : **{str(curr_eff)}**\nQuality : **{cond_list[cond]}**\nHealthy Effort : **{curr_eff*5}**"
        curr_eff *= 5
        if cond != 4:
            curr_eff = condup(curr_eff,cond)
            final_txt += f"\nMint Effort : **~{str(curr_eff)}**"
    else :
        final_txt += f"Effort : **{str(curr_eff)}**\nQuality : **{cond_list[cond]}**\n`Card is Healthy`"
        if cond != 4:
            curr_eff = condup(curr_eff,cond)
            final_txt += f"\nMint Effort : **~{str(curr_eff)}**"
    base_val = int(desc[2].split("\n")[1].split(" Base")[0])
    if cond != 4:
        base_val = basecal(base_val,cond)
    grabber_r = desc[-1].split("Grabber")[0].split("(")[-1][0]
    dropper_r = desc[-1].split("Dropper")[0].split("(")[-1][0]
    if grabber_r != "F" or dropper_r != "F":
        t_godsub = godup(grabber_r,base_val) + godup(dropper_r,base_val)
        t_godsub += round(t_godsub/4)
        final_txt += f"\n`Without G/D : {str(curr_eff-t_godsub)} (-{str(t_godsub)})`"
    if sty_l:
        lis = [base_val*1.5, base_val*0.75, base_val*0.2, base_val*0.95]
        a = lis.index(closest(lis, sty_l))
        if a == 0:
            curr_eff -= round(base_val*0.9375*2)
        elif a == 1:
            curr_eff -= round(base_val*0.9375)
        elif a == 2:
            curr_eff -= round(base_val*0.25)
        else:
            curr_eff -= round(base_val*1.1875)
    final_txt += f"\n\n**Dye and Frame**\n"
    final_txt += f"""```py\n  Frame          : ~{str(round(base_val*0.9375)+curr_eff)} (+{str(round(base_val*0.9375))})
  Dye            : ~{str(round(base_val*0.25)+curr_eff)} (+{str(round(base_val*0.25))})
  Mystic Dye     : ~{str(round(base_val*0.9375)+curr_eff)} (+{str(round(base_val*0.9375))})
  Dye & frame    : ~{str(round(base_val*0.9375)+curr_eff+round(base_val*0.25))} (+{str(round(base_val*0.9375)+round(base_val*0.25))})
  Mystic & frame : ~{str(round(base_val*0.9375*2)+curr_eff)} (+{str(round(base_val*0.9375*2))})\n```"""
    final_txt += "\n**Vanity and Toughness**"
    vanity_r = desc[-1].split("Vanity")[0].split("(")[-1][0]
    vanity_v = int(desc[-1].split(" Vanity")[-2].split("\n")[-1].split(" ")[0].replace('\xc2\xa0', ''))
    if vanity_r == "F":
        final_txt += "\n```py\n   Vanity (F)     :  Null"
    else:
       vanity_rang = vanity_c(vanity_r,base_val)
       final_txt += f"\n```py\n  Vanity ({vanity_r})     :  {vanity_rang}" 
    m_vanity = int(vanity_c("A",base_val).split(" - ")[-1])
    final_txt += f"""\n  Max Vanity (A) :  {m_vanity}"""
    tough_r = desc[-1].split("Toughness")[0].split("(")[-1][0]
    tough_v = int(desc[-1].split(" Toughness")[-2].split("\n")[-1].split(" ")[0].replace('\xc2\xa0', ''))
    max_t = int(tough_c(tough_r,base_val))
    if tough_r != "S":
        final_txt += f"""\n  Max Tough. (S) :  {tough_c("S",base_val)}```"""
        max_t = int(tough_c("S",base_val))
    else:
        final_txt += "```"
    max_v = int(vanity_rang.split(" - ")[-1])
    final_txt += "\n**Max Effort**\n```py"
    final_txt += f"\n  Vanity ({vanity_r})          : ~{round(base_val*0.9375*2+(max_v-vanity_v)*0.25)+curr_eff+max_v-vanity_v}"
    final_txt += f"\n  Vanity {vanity_r} + Tough. S : ~{round(base_val*0.9375*2+(max_t+max_v-tough_v-vanity_v)*0.25)+curr_eff+max_v+max_t-tough_v-vanity_v}"
    final_txt += f"""\n  Vanity A + Tough. S : ~{round(base_val*0.9375*2+(max_t+m_vanity-tough_v-vanity_v)*0.25)+curr_eff+m_vanity- vanity_v+max_t-tough_v}\n```"""
    range_i, range_f = curr_eff, curr_eff
    for i in range(4-cond):
        range_i += round(range_i*89/100)-5
        range_f += round(range_f*89/100)+5
    return [final_txt, round((range_f-range_i)/2)]


def godup(rank, base_val):
    if rank == "F":
        return 0
    return round(base_val*0.1)

def tough_c(rank,base):
    if rank == "S":
        return str(round(base/4))
    elif rank == "A":
        return str(round(base/5))
    elif rank == "B":
        return str(round(base/6.5))
    elif rank == "C":
        return str(round(base/10))
    elif rank == "D":
        return str(round(base/20))
    return "0"

def vanity_c(rank,base):
    if rank == "S":
        return str(round(base*0.5))
    elif rank == "A":
        return str(round(base*0.375))+" - "+str(round(base*0.5))
    elif rank == "B":
        return str(round(base*0.25))+" - "+str(round(base*0.375))
    elif rank == "C":
        return str(round(base*0.125))+" - "+str(round(base*0.25))
    elif rank == "D":
        return "0 - "+str(round(base*0.125))
    
    
    
    

class EffortCalculator(commands.Cog):
    """
    Automatically calculates the efforts. You can set it for your server with autoeff-set command.
    """
    def __init__(self, bot):
        self.bot = bot
        self.elist = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        self.plus_emj = "plus:863021349652004884"
        self.cond_chart = "Use corresponding number to your card's quality : \n\n   *0 - Damaged* (☆☆☆☆)\n   *1 - Poor* (★☆☆☆)\n   *2 - Good* (★★☆☆)\n   *3 - Excellent* (★★★☆)\n   *4 - Mint* (★★★★)\n\n**Note :**"
        
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            return
        if message.channel.type == discord.ChannelType.private:
            return
        if not message.embeds:
            return
        if not(message.guild.me.guild_permissions.use_external_emojis):
            return
        if message.guild.id not in self.bot.eff_channels:
            return
        if message.channel.id != self.bot.eff_channels[message.guild.id]:
            return
        if message.author.id == 646937666251915264 and message.embeds[0].title == "Worker Details":
            msg = message
            try:
                await msg.add_reaction(self.plus_emj)
            except:
                return
            def check_r(reaction,user):
                return user != self.bot.user and str(reaction.emoji) == f"<:{self.plus_emj}>" and reaction.message.id == message.id
            try:
                reaction, ruser = await self.bot.wait_for('reaction_add', timeout = 20 ,check = check_r)
            except:
                return
            e_dict = msg.embeds[0].to_dict()
            style = e_dict['description'].split(" Style")[-2].split("\n")[-1].split(" ")[0]
            style = style.replace('\xc2\xa0', '')
            base_eff =  int(e_dict['description'].split("\n\n")[2].split("\n")[1].split(" Base")[0])
            if int(style) == 0 and base_eff < 56:
                embed = discord.Embed(colour = self.bot.ecolor, title = "Effort Calculator", description = self.cond_chart)
                embed.set_footer(text = "React with emojis below.")
                e_msg = await msg.reply(embed = embed, mention_author = False)
                for e in self.elist:
                    await e_msg.add_reaction(e)
                def check_rl(reaction,user):
                    return ruser == user and str(reaction.emoji) in self.elist and reaction.message.id == e_msg.id
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout = 20 ,check = check_rl)
                except:
                    n_embed = discord.Embed(colour = self.bot.ecolor, title = "Effort Calculator", description = self.cond_chart[:-10:] + "\n" + "⏱️ Session timed out! Retry.")
                    await e_msg.edit(embed = n_embed)
                    try:
                        await e_msg.clear_reactions()
                    except:
                        pass
                    return
                cond = self.elist.index(str(reaction))
                desc = e_dict['description']
                im_url = e_dict['thumbnail']['url']
                descript = autoeff(cond,desc)
                n_embed = discord.Embed(colour = self.bot.ecolor, title = "Effort Calculator", description = descript[0])
                n_embed.set_thumbnail(url = im_url)
                n_embed.set_footer(text = f"These are approx. values, actual values may vary ±{str(descript[1] or 1)}.")
                await e_msg.edit(embed = n_embed)
                try:
                    await e_msg.clear_reactions()
                except:
                    pass
                return
            else:
                cond = 4
                desc = e_dict['description']
                im_url = e_dict['thumbnail']['url']
                n_embed = discord.Embed(colour = self.bot.ecolor, title = "Effort Calculator", description = autoeff(cond,desc,int(style))[0])
                n_embed.set_thumbnail(url = im_url)
                n_embed.set_footer(text = "These are approx. values, actual values may vary ±1.")
                await msg.reply(embed = n_embed, mention_author = False)
    
    
    @commands.command(name = "effort", aliases = ["eff"])
    async def eff_calc(self, ctx):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if not(ctx.message.reference):
            return
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if not message.embeds:
            return
        ruser = ctx.author
        if message.author.id == 646937666251915264 and message.embeds[0].title == "Worker Details":
            msg = message
            e_dict = msg.embeds[0].to_dict()
            style = e_dict['description'].split(" Style")[-2].split("\n")[-1].split(" ")[0]
            style = style.replace('\xc2\xa0', '')
            base_eff =  int(e_dict['description'].split("\n\n")[2].split("\n")[1].split(" Base")[0])
            if int(style) == 0 and base_eff < 56:
                embed = discord.Embed(colour = self.bot.ecolor, title = "Effort Calculator", description = self.cond_chart)
                embed.set_footer(text = "React with emojis below.")
                e_msg = await msg.reply(embed = embed, mention_author = False)
                for e in self.elist:
                    await e_msg.add_reaction(e)
                def check_rl(reaction,user):
                    return ruser == user and str(reaction.emoji) in self.elist and reaction.message.id == e_msg.id
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout = 20 ,check = check_rl)
                except:
                    n_embed = discord.Embed(colour = self.bot.ecolor, title = "Effort Calculator", description = self.cond_chart[:-10:] + "\n" + "⏱️ Session timed out! Retry.")
                    await e_msg.edit(embed = n_embed)
                    try:
                        await e_msg.clear_reactions()
                    except:
                        pass
                    return
                cond = self.elist.index(str(reaction))
                desc = e_dict['description']
                im_url = e_dict['thumbnail']['url']
                descript = autoeff(cond,desc)
                n_embed = discord.Embed(colour = self.bot.ecolor, title = "Effort Calculator", description = descript[0])
                n_embed.set_thumbnail(url = im_url)
                n_embed.set_footer(text = f"These are approx. values, actual values may vary ±{str(descript[1] or 1)}.")
                await e_msg.edit(embed = n_embed)
                try:
                    await e_msg.clear_reactions()
                except:
                    pass
                return
            else:
                cond = 4
                desc = e_dict['description']
                im_url = e_dict['thumbnail']['url']
                n_embed = discord.Embed(colour = self.bot.ecolor, title = "Effort Calculator", description = autoeff(cond,desc,int(style))[0])
                n_embed.set_thumbnail(url = im_url)
                n_embed.set_footer(text = "These are approx. values, actual values may vary ±1.")
                await msg.reply(embed = n_embed, mention_author = False)
    
    
    @commands.command(name = "autoeff-set", aliases = ["autoeffort-set"])
    async def autoeff_set(self, ctx):
        if ctx.author.bot:
            return
        if ctx.channel.type == discord.ChannelType.private:
            return
        if not(ctx.message.author.guild_permissions.administrator):
            await ctx.channel.send(f"<@{str(ctx.author.id)}>, you do not have proper permissions to use this command.")
            return
        unset_cond = False
        if ctx.guild.id in self.bot.eff_channels:
            if ctx.channel.id == self.bot.eff_channels[ctx.guild.id]:
                unset_cond = True
        if unset_cond:
            temp_doc = {"autoec" : ctx.channel.id}
            self.bot.serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$unset" : temp_doc})
            self.bot.eff_channels.pop(ctx.guild.id)
            await ctx.channel.send(f'<@{ctx.author.id}>, you have unset auto effort calculate channel.')
            return
        temp_doc = {"autoec" : ctx.channel.id}
        self.bot.serverdat_obj.update_one({"_id" : ctx.guild.id}, {"$set" : temp_doc})
        self.bot.eff_channels[ctx.guild.id] = ctx.channel.id
        embed = discord.Embed(colour = self.bot.ecolor, description = f'Auto effort calculating channel set to <#{str(ctx.channel.id)}> channel.')
        await ctx.channel.send(embed = embed)
    
def setup(bot):
    bot.add_cog(EffortCalculator(bot))
