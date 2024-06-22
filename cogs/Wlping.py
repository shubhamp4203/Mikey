
import asyncio
import cv2 as cv
import time
from difflib import SequenceMatcher
import aiohttp
import numpy as np
import pytesseract
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from num2words import num2words


class Wlping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id not in [569168901204606996, 761923749179162675, 646937666251915264]:
            return
        if msg.channel.id != 870275991883358278:
            return
        if not msg.attachments:
            return
        if "dropping" not in msg.content:
            return
        url = msg.attachments[0].url

        def are_sim(a, b):
            return SequenceMatcher(None, a, b).ratio() * 100

        def check_card_series(serieslist, wldict):
            for series in serieslist:
                for series_data in wldict.keys():
                    if are_sim(series_data.lower(), series) > 80:  # matchrate
                        if 100 * len(series) / (len(series) + len(series_data)) > 45 and 100 * len(series) / (len(series) + len(series_data)) < 60:
                            series = series_data
                            return series
            return

        def check_card_char(clist, wl_dict, s_name):
            for char in clist:
                for name in wl_dict[s_name]:
                    if are_sim(name.lower(), char) > 80:  # matchrate
                        if 100 * len(char) / (len(char) + len(name)) > 45 and 100 * len(char) / (len(char) + len(name)) < 60:
                            index = num2words(c_list.index(char) + 1)
                            char = name
                            return char, index
                        return -1,-1
            return -1,-1

        async def ocrmainchar(img):
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            result = pytesseract.image_to_string(img, lang='eng', config='--psm 7')
            result = result.replace("\n", " ")
            return textfilter(result)

        async def ocrmainseries(img):
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            result = pytesseract.image_to_string(img, lang='eng', config='--psm 11')
            result = result.replace("\n", " ")
            return textfilter(result)

        def textfilter(text):
            ret_str = ""
            for letter in text:
                if letter.isalnum() or letter == " ":
                    ret_str += letter.lower()
            return ret_str.strip()

        async def getimg(im_url):
            async with aiohttp.ClientSession() as session:
                async with session.get(im_url) as resp:
                    im_bytes = await resp.read()
                    return im_bytes

        arr = np.asarray(bytearray(await getimg(url)), dtype=np.uint8)
        img = cv.imdecode(arr, -1)
        #img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        '''cv.imshow('test', img)
        cv.waitKey(0),
        cv.destroyAllWindows()'''


        async def cardocrseries():
            if img.shape == (419, 836, 4):
                img1 = img[314:363, 47:233]
                img2 = img[314:363, 321:507]
                img3 = img[314:363, 595:782]
                serieslist = await asyncio.gather(ocrmainseries(img1), ocrmainseries(img2), ocrmainseries(img3))
                return serieslist
            elif img.shape == (419, 1110, 4):
                img1 = img[314:363, 47:233]
                img2 = img[314:363, 321:507]
                img3 = img[314:363, 595:782]
                img4 = img[314:363, 872:1060]
                serieslist = await asyncio.gather(ocrmainseries(img1),
                              ocrmainseries(img2),
                              ocrmainseries(img3),
                              ocrmainseries(img4))
                return serieslist
            return False

        async def cardocrchar():
            if img.shape == (419, 836, 4):
                img1 = img[56:105, 54:222]
                img2 = img[56:105, 328:507]
                img3 = img[56:105, 601:771]
                char_list = await asyncio.gather(ocrmainchar(img1),
                             ocrmainchar(img2),
                             ocrmainchar(img3))
                return char_list
            elif img.shape == (419, 1110, 4):
                img1 = img[56:105, 54:223]
                img2 = img[56:105, 326:507]
                img3 = img[56:105, 601:771]
                img4 = img[56:105, 873:1045]
                char_list = await asyncio.gather(ocrmainchar(img1),
                             ocrmainchar(img2),
                             ocrmainchar(img3),
                             ocrmainchar(img4))
                return char_list
            return False


        initial = time.time() * 1000
        #s_list = await cardocrseries()
        #c_list = await cardocrchar()
        results = await asyncio.gather(cardocrchar(), cardocrseries())
        c_list = results[0]
        s_list = results[1]
        print(s_list)
        sname = check_card_series(s_list, wldict)
        if sname not in wldict.keys():
            return
        cname, index = check_card_char(c_list, wldict, sname)
        if (cname == -1 or index == -1):
            return

        if cname in wldict[sname]:
            if wldict[sname][cname] == 925775130850889768:
                rarity = "A `Common Card`"
            elif wldict[sname][cname] == 925775075783901236:
                rarity = "An `Epic Card`"
            elif wldict[sname][cname] == 925775033622724618:
                rarity = "A `Rare Card`"
            else:
                rarity = "A `Legendary Card`"
            finaltime = time.time() * 1000
            await msg.reply(
                f":{index}: <@&{wldict[sname][cname]}> {rarity} **{cname}** has dropped!!\nTime Taken: {round(finaltime - initial)}ms")

def setup(bot):
    bot.add_cog(Wlping(bot))
