import json
import discord
from discord.ext import commands

wllb_dict = {}
with open("lb_data.json", "r") as fr:
    msgdict = json.load(fr)




class wllb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id != 646937666251915264:
            return
        if not msg.embeds:
            return
        if "Character Lookup" not in msg.embeds[0].title:
            return
        desp = msg.embeds[0].description
        verify = desp.split("·")[2].split("\n")[1]
        if verify == "Koibito ":
            wl = desp.split("·")[4].split("\n")[0].split("**")[1].replace(",", "")
            wl = int(wl)
            char_name = desp.split("·")[1].split("\n")[0].split("**")[1]
            series_name = desp.split("·")[2].split("\n")[0].split("**")[1]
        else:
            wl = desp.split("·")[3].split("\n")[0].split("**")[1].replace(",", "")
            wl = int(wl)
            char_name = desp.split("·")[1].split("\n")[0].split("**")[1]
            series_name = desp.split("·")[2].split("\n")[0].split("**")[1]

        if wl <= 299:
            return

        wllb_dict[char_name] = {series_name: wl}
        lot = []
        for k, v in wllb_dict.items():
            k_, v_ = next(iter(v.items()))
            lot.append((v_, k_, k))
        sorted_dict = {a: {b: c} for c, b, a in sorted(lot, reverse=True)}
        text = ""
        j = 0
        l = 1
        for i in sorted_dict.keys():
            for k in sorted_dict[i].keys():
                text += f"{j + 1}. `{sorted_dict[i][k]}` - {k} - **{i}**\n"
                j += 1
                if j%20 == 0:
                    msgdict[l] = text
                    l += 1
                    text = ""


        with open("lb_data.json", "w") as f:
            json.dump(msgdict, f, indent=4)








def setup(bot):
    bot.add_cog(wllb(bot))
