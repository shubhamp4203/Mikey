import discord
from discord.ext import commands
from discord.ui import Button, View
from datetime import datetime

class Myview(discord.ui.View):
    def __init__(self, ctx, timeout=30):
        super().__init__()
        self.ctx = ctx
        self.timeout = timeout

    async def interaction_check(self, interaction):
        if interaction.user != self.ctx.author:
            return False
        else:
            return True

    async def on_timeout(self):
        self.clear_items()
        return

class shardm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.is_owner()
    @commands.command(name="shards", aliases=[])
    async def show_shards(self, ctx):
        if ctx.channel.type == discord.ChannelType.private:
            return
        shards_dict = {}
        shards_det = self.bot.shards
        m_shard = ctx.guild.shard_id #self.bot.get_guild(863010215045234688).shard_id
        for shard_id in shards_det:
            shards_dict[shard_id] = {"servers" : 0, "members" : 0}
            shards_dict[shard_id]["status"] = not shards_det[shard_id].is_closed() #true when running
            if shards_dict[shard_id]["status"]:
                shards_dict[shard_id]["ping"] = round(shards_det[shard_id].latency*1000) #latency in ms
            else:
                shards_dict[shard_id]["ping"] = "--"
            shards_dict[shard_id]["ratel"] = shards_det[shard_id].is_ws_ratelimited() #true when ratelimited
        for guild in self.bot.guilds:
            shards_dict[guild.shard_id]["servers"] += 1
            shards_dict[guild.shard_id]["members"] += guild.member_count
        t_pno = 1
        shard_dat_dict = {1:""}
        for shard_id, shardcount in zip(shards_dict.keys(), range(1, len(shards_dict)+1)):
            if t_pno*10 < shardcount:
                t_pno += 1
                shard_dat_dict[t_pno] = ""
            shard_dat_dict[t_pno] += f"{'**' if m_shard==shard_id else ''}{':no_entry:' if shards_dict[shard_id]['ratel'] else ':green_circle:' if shards_dict[shard_id]['status'] else ':red_circle:'} `#{shard_id}` Ping : `{shards_dict[shard_id]['ping']}ms` Servers : `{shards_dict[shard_id]['servers']}` Members : `{shards_dict[shard_id]['members']}`{'**' if m_shard==shard_id else ''}\n"
        lembed = discord.Embed(title="Shards", description=f"\n{shard_dat_dict[1]}\n", color=0x00FFB7)
        await ctx.reply(embed=lembed)
    
    @commands.is_owner()
    @commands.command(name="shard", aliases=[])
    async def show_one_shards(self, ctx, shard_id : int):
        if ctx.channel.type == discord.ChannelType.private:
            return
        shard = self.bot.get_shard(shard_id)
        m_shard = ctx.guild.shard_id #self.bot.get_guild(863010215045234688).shard_id
        if not shard:
            return
        lembed = discord.Embed(title=f"Shard Info #{shard_id} {'👑' if m_shard==shard_id else ''}", color=0x00FFB7)
        lembed.add_field(name="Shard Id", value=shard_id, inline=True)
        lembed.add_field(name="Ping", value=round(shard.latency*1000) if not shard.is_closed() else "--", inline=True)
        lembed.add_field(name="Master Shard", value = str(m_shard == shard_id), inline=True)
        lembed.add_field(name="Running", value=str(not shard.is_closed()), inline=True)
        lembed.add_field(name="Rate Limited", value=str(shard.is_ws_ratelimited()), inline=True)
        but_conn = Button(label="Connect", custom_id="connect",style=discord.ButtonStyle.blurple)
        but_disc = Button(label="Disconnect", custom_id="disconnect",style=discord.ButtonStyle.blurple)
        but_reco = Button(label="Reconnect", custom_id="reconnect",style=discord.ButtonStyle.blurple)
        view = Myview(ctx, timeout=100)
        view.add_item(but_conn)
        view.add_item(but_disc)
        view.add_item(but_reco)
        async def b1_callback(interaction):
            foot = "Shard is already connected."
            cond = 1
            if shard.is_closed():
                try:
                    await shard.connect()
                    foot = "Shard connected successfully."
                except:
                    foot = "Some error occured while connecting."
                    cond = 0
            else:
                cond = 0
            lembed = interaction.message.embeds[0]
            lembed.set_field_at(3, name="Running", value = not shard.is_closed(), inline=True)
            lembed.set_footer(text = foot)
            if cond:
                but_disc.disabled = False
                but_reco.disabled = False
                but_conn.disabled = True
            await interaction.response.edit_message(embed=lembed, view=view)
            return
        async def b2_callback(interaction):
            foot  = "Shard is already disconnected."
            cond = 1
            if not shard.is_closed():
                try:
                    await shard.disconnect()
                    foot = "Shard disconnected successfully."
                except:
                    foot = "Some error occured while disconnecting."
                    cond = 0
            else:
                cond = 0
            lembed = interaction.message.embeds[0]
            lembed.set_field_at(3, name="Running", value = not shard.is_closed(), inline=True)
            lembed.set_footer(text = foot)
            if cond:
                but_disc.disabled = True
                but_reco.disabled = True
                but_conn.disabled = False
            await interaction.response.edit_message(embed=lembed, view=view)
            return
        async def b3_callback(interaction):
            foot = "Nothing happened."
            cond = 1
            try:
                await shard.reconnect()
                foot = "Shard reconnected successfully."
            except:
                foot = "Some error occured while reconnecting."
                cond = 0
            lembed = interaction.message.embeds[0]
            lembed.set_field_at(3, name="Running", value = not shard.is_closed(), inline=True)
            lembed.set_footer(text = foot)
            if cond:
                but_disc.disabled = False
                but_reco.disabled = False
                but_conn.disabled = True
            await interaction.response.edit_message(embed=lembed, view=view)
            return
        but_conn.callback = b1_callback
        but_disc.callback = b2_callback
        but_reco.callback = b3_callback
        if (shard_id == m_shard):
            but_disc.disabled = True
        if shard.is_closed():
            but_disc.disabled = True
            but_reco.disabled = True
        else:
            but_conn.disabled = True
        but_conn.disabled = True
        but_disc.disabled = True
        but_reco.disabled = True
        await ctx.reply(embed=lembed, view = view)

def setup(bot):
    bot.add_cog(shardm(bot))
