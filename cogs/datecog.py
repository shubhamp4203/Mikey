import cv2 as cv
import urllib
import numpy as np
import discord
import math
import time
from discord.ext import commands
from discord.ext.commands import command
import asyncio
import aiohttp

#Queue

cddict = {}
db_pro = False
cd_pu = 0

## Setting ##

enabled_roles = [863034710674505728]
enabled_channels = [863010215045234691]
ecolor = 0x00FFFF

# 0 => Ring will not affect the choosing of the final solution
# 1 => Ring will be included if possible, prioritizes survival
# 2 => Ring will be included if possible, prioritizes ring
#need_ring = 1
# Aims to get to the airplane instead of home
# Not optimized rn
airplane = False

depth = 25
max_iteration = 6942069
debug = False

# default: [100, 50, 50, 75, 100]
initial_resource = [100, 50, 50, 75, 100]
# default: 14, 5, 1
cur_row, cur_col, cur_turn = 14, 5, 1

respawn_matrix = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
]


## Data ##

lastrunstrings = ""
lastrunlink = ""
lastuser = 0
locationlist = list("gtpsjcnmwbfah012")

locationy = [
    169,
    203,
    244,
    292,
    352,
    427,
    524
]

locationx = [
    [278, 339, 400, 460, 521],
    [268, 334, 400, 465, 531],
    [255, 327, 400, 472, 544],
    [240, 320, 400, 479, 559],
    [221, 310, 400, 489, 578],
    [197, 298, 400, 501, 602],
    [165, 282, 400, 517, 634]
]

roadblocky = [
    184,
    197,
    215,
    232,
    256,
    274,
    300,
    325,
    358,
    388,
    432,
    470,
    527
]

roadblockx = [
    [306, 366, 434, 494],
    [293, 355, 382, 444, 507],
    [298, 363, 436, 502],
    [282, 352, 381, 449, 517],
    [287, 360, 440, 513],
    [271, 346, 378, 452, 528],
    [276, 356, 444, 524],
    [257, 341, 375, 459, 543],
    [261, 350, 449, 538],
    [238, 331, 372, 466, 560],
    [242, 343, 457, 558],
    [216, 322, 368, 477, 584],
    [218, 335, 465, 582]
]

location_emojis = {
    # Locations
    "g": "⛽",
    "t": "🌮",
    "p": "🍝",
    "s": "🥪",
    "j": "🧃",
    "c": "☕",
    "n": "🍹",
    "m": "🎭",
    "w": "🎡",  # wheel
    "b": "💃",
    "f": "🌼",

    "a": "✈",
    "h": "🏠",
    "0": "🌲",
    "1": "💍",
    "2": "🛍",

    "u": "🔼",
    "d": "🔽",
    "l": "◀️",
    "r": "▶️"
}

denotations = {
    # Locations
    "g": "gas",
    "t": "taco",
    "p": "pasta",
    "s": "sandwich",
    "j": "juice",
    "c": "coffee",
    "n": "night club",
    "m": "mask",
    "w": "fair",  # wheel
    "b": "ballroom",
    "f": "flower",

    # Special Locations
    "a": "airplane",
    "h": "home",
    "0": "tree",
    "1": "ring",
    "2": "shopping",

    # Movements and directions
    "u": "up",
    "d": "down",
    "l": "left",
    "r": "right"
    # NOTE:
    # Ring is denoted 1
    # Shopping is denoted 2
    # Fair is denoted w
}

updates = {
    # Locations
    "g": [100, -4, -6, -8, -4],
    "t": [0, 56, -6, -8, -4],
    "p": [0, 56, -6, -8, -4],
    "s": [0, 36, 14, -8, -4],
    "j": [0, -4, 54, -8, -4],
    "c": [0, -4, 54, -8, -4],
    "n": [0, -4, 34, 32, -4],
    "m": [0, -4, -6, 52, -4],
    "w": [0, 16, 14, 32, -4],
    "b": [0, -14, -21, 92, -4],
    "f": [0, -4, -6, 92, -4],

    # Special Locations
    "a": [0, -4, -6, -18, -4],
    "h": [0, 0, 0, 0, 0],
    "0": [0, 0, 0, 0, 0],
    "1": [0, -4, -6, -8, -4],
    "2": [0, -4, -6, -8, -4],

    # Movements and directions
    "u": [-10, -4, -6, -8, -4],
    "d": [-10, -4, -6, -8, -4],
    "l": [-10, -4, -6, -8, -4],
    "r": [-10, -4, -6, -8, -4]
}


async def getimg(im_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(im_url) as resp:
            im_bytes =  await resp.read()
            return im_bytes

## Functions ##
async def getinput(img_url):
    global locationlist, locationx, locationy, roadblockx, roadblocky, debug
    startedmoving = False
    try:
        #req = urllib.request.urlopen(img_url)
        #arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        arr = np.asarray(bytearray(await getimg(img_url)), dtype=np.uint8)
        img = cv.imdecode(arr, -1)
        if debug:
            print(img.shape)
        if not img.shape == (600, 800, 4):
            return "", "", "", ""
        elif not (img[130][700] == [0, 255, 0, 255]).all():
            startedmoving = True
    except Exception as e:
        if debug:
            print("get input error:", e)
        return "", "", "", ""

    _location_string = ""
    radius = 16
    for i in range(len(locationy)):
        for j in range(len(locationx[i])):
            curry, currx = locationy[i], locationx[i][j]
            sub_image = img[curry-radius:curry+radius, currx-radius:currx+radius]
            highest_res = -2147483649
            highest_location = "0"
            for k in locationlist:
                filename = f"./locations/{k}.png"
                temp_img = cv.imread(filename, cv.IMREAD_UNCHANGED)
                res = cv.matchTemplate(sub_image, temp_img, cv.TM_CCOEFF_NORMED)
                if res[0][0] > highest_res:
                    highest_res = res[0][0]
                    highest_location = k
            _location_string = _location_string + highest_location

    _roadblock_string = ""

    for i in range(len(roadblocky)):
        for j in range(len(roadblockx[i])):
            curry, currx = roadblocky[i], roadblockx[i][j]
            if (img[curry, currx] == [113, 86, 53, 255]).all():
                # has a open road
                _roadblock_string = _roadblock_string + "0"
            else:
                _roadblock_string = _roadblock_string + "1"

    _direction = ""
    if (img[581][395] == [250, 108, 47, 255]).all():
        _direction = "l"
    else:
        _direction = "r"

    return _location_string, _roadblock_string, _direction, startedmoving


# r = row
# c = col
# m = move
# d = direction
def move(r, c, m, d):
    if m == "u":
        if d == "d":
            return -1, -1
        if r % 2 == 1 and not r <= 2:
            return r-2, c
        elif r % 2 == 0 and not r <= 1:
            if d == "l":
                return r-1, c-1
            else:
                return r-1, c+1
        else:
            return -1, -1
    elif m == "d":
        if d == "u":
            return -1, -1
        if r % 2 == 1 and not r >= 12:
            return r+2, c
        elif r % 2 == 0 and not r >= 13:
            if d == "r":
                return r+1, c+1
            else:
                return r+1, c-1
        else:
            return -1, -1
    elif m == "l":
        if d == "r":
            return -1, -1
        if c % 2 == 1 and not c <= 2:
            return r, c-2
        elif c % 2 == 0 and not c <= 1:
            if d == "u":
                return r-1, c-1
            else:
                return r+1, c-1
        else:
            return -1, -1
    elif m == "r":
        if d == "l":
            return -1, -1
        if c % 2 == 1 and not c >= 8:
            return r, c+2
        elif c % 2 == 0 and not c >= 9:
            if d == "u":
                return r-1, c+1
            else:
                return r+1, c+1
        else:
            return -1, -1
    else:
        return -1, -1


def blocked(r, c, roadblocks):
    try:
        isblocked = roadblocks[r-1][(c-1)//2] == "1"
        return isblocked
    except:
        return False


def getlocations(r, c, turn, respawn, locations):
    rv = []
    if r == 0:
        rv.append("0")
        rv.append(locations[0][c//2] if turn > respawn[0][c//2] else "0")
    elif r == 14:
        rv.append(locations[6][c//2] if turn > respawn[6][c//2] else "0")
        rv.append("0")
    elif r % 2 == 0:
        rv.append(locations[(r//2)-1][c//2] if turn > respawn[(r//2)-1][c//2] else "0")
        rv.append(locations[(r//2)][c//2] if turn > respawn[(r//2)][c//2] else "0")
    else:
        if c == 0:
            rv.append("0")
            rv.append(locations[(r//2)][0] if turn > respawn[(r//2)][0] else "0")
        elif c == 10:
            rv.append(locations[(r//2)][4] if turn > respawn[(r//2)][4] else "0")
            rv.append("0")
        else:
            rv.append(locations[(r//2)][(c//2)-1] if turn > respawn[(r//2)][(c//2)-1] else "0")
            rv.append(locations[(r//2)][(c//2)] if turn > respawn[(r//2)][(c//2)] else "0")
    return rv


def getmoves(r, c, d,  turn, respawn, _locations, _roadblocks):
    loc = []
    loc = loc + getlocations(r, c, turn, respawn, _locations)

    for i in ["u", "d", "l", "r"]:
        _r, _c = move(r, c, i, d)

        if _r < 0 or _c < 0:
            continue
        if not blocked(_r, _c, _roadblocks):
            loc.append(i)

    return loc


def createsolution(moves, resources, alive, iteration):
    _resources = resources.copy()
    timeremain = _resources.pop()
    if "h" in moves:
        _resources[1] -= 4
        _resources[2] -= 6
        _resources[3] -= 8

    rv = {
        "moves": moves,
        "resources": _resources,
        "home": "h" in moves,
        "ring": "1" in moves,
        "shopping": "2" in moves,
        "alive": alive,
        "iteration": iteration
    }
    return rv


def comparesolution(oldsol, newsol, need_ring):
    global airplane

    if oldsol == {}:
        return True

    if not oldsol["alive"] and newsol["alive"]:
        return need_ring < 2 or newsol["ring"]

    oldscore = sum(oldsol["resources"][1:]) * len(oldsol["moves"]) / 25

    if oldsol["shopping"]:
        oldscore += 180
    if oldsol["ring"] and need_ring > 0:
        oldscore += 1000

    newscore = sum(newsol["resources"][1:]) * len(newsol["moves"]) / 25

    if newsol["shopping"]:
        newscore += 180
    if newsol["ring"] and need_ring > 0:
        newscore += 1000

    return newscore > oldscore


def updaterespawn(respawn, turn, r, c, i, isspecial):
    rv = [x[:] for x in respawn]
    _r, _c = -1, -1
    if r == 0:
        _r, _c = 0, c//2
    elif r == 14:
        _r, _c = 6, c//2
    elif r % 2 == 0:
        if i == 0:
            _r, _c = r//2 - 1, c//2
        else:
            _r, _c = r//2, c//2
    else:
        if c == 0:
            _r, _c = r//2, 0
        elif c == 10:
            _r, _c = r//2, 4
        else:
            if i == 0:
                _r, _c = r//2, c//2-1
            else:
                _r, _c = r//2, c//2
    rv[_r][_c] = 25 if isspecial else turn + 10
    return rv


async def date(turn, resources, respawn, r, c, d, moves, globalv, need_ring):
    #await asyncio.sleep(0)
    global updates, max_iteration, depth, airplane
    await asyncio.sleep(0)
    try:
        if debug:
            print(resources, r, c, moves)
    except:
        pass
    if globalv["iterations"] >= max_iteration:
        return
    globalv["iterations"] += 1

    for i in range(len(resources)-1):
        if resources[i] <= 0:
            if "1" in moves and need_ring >= 2:
                sol = createsolution(moves, resources, False, globalv["iterations"])
                if comparesolution(globalv["bestsolution"], sol, need_ring):
                    globalv["bestsolution"] = sol
                globalv["totalsol"] += 1
            return
    if turn > min(25, depth) or resources[len(resources)-1] <= 0:
        if not airplane:
            sol = createsolution(moves, resources, True, globalv["iterations"])
            if comparesolution(globalv["bestsolution"], sol, need_ring):
                globalv["bestsolution"] = sol
            globalv["totalsol"] += 1
        return

    validmoves = getmoves(r, c, d, turn, respawn, globalv["locations"], globalv["roadblocks"])
    try:
        if debug:
            print(validmoves)
    except:
        pass
    for i in range(len(validmoves)):
        if validmoves[i] == "0":
            continue

        updatedresources = []
        updatelist = updates[validmoves[i]]
        updatedmoves = moves + [validmoves[i]]

        for j in range(len(resources)):
            updatedresources.append(min(100, resources[j]+updatelist[j]))

        if validmoves[i] == "a":
            if airplane:
                dead = False
                for i in range(len(resources) - 1):
                    if resources[i] <= 0:
                        dead = True
                if dead:
                    continue
                sol = createsolution(updatedmoves, updatedresources, True, globalv["iterations"])
                globalv["totalsol"] += 1

                if comparesolution(globalv["bestsolution"], sol, need_ring):
                    globalv["bestsolution"] = sol
            continue

        if validmoves[i] == "h":
            if not airplane:
                sol = createsolution(updatedmoves, updatedresources, True, globalv["iterations"])
                globalv["totalsol"] += 1

                if comparesolution(globalv["bestsolution"], sol, need_ring):
                    globalv["bestsolution"] = sol
            continue

        if i < 2:
            await date(turn+1, updatedresources, updaterespawn(respawn, turn, r, c, i, validmoves[i] in ["f", "1", "2"]), r, c, d, updatedmoves, globalv, need_ring)
        else:
            newr, newc = move(r, c, validmoves[i], d)
            await date(turn+1, updatedresources, respawn, newr, newc, validmoves[i], updatedmoves, globalv, need_ring)

def stohr(s_econds):
    days = s_econds//(24*3600)
    s_econds %= (24*3600)
    hr = s_econds//3600
    s_econds %= 3600
    min = s_econds//60
    s_econds %= 60
    s_econds,hr,min,days = str(s_econds)+"s",str(hr)+"hr ",str(min)+"min ", str(days)+"d "
    return min+s_econds

async def rundate(img_url, msg, need_ring, uid):
    global cur_turn, initial_resource, respawn_matrix, cur_row, cur_col, lastrunstrings, lastrunlink, cddict, db_pro, lastuser

    starttime = time.time()

    location_string, roadblock_string, direction, startedmoving = await getinput(img_url)

    if len(location_string) != 35 or len(roadblock_string) != 58:
        return False, "", ""

    if startedmoving:
        print(location_string, roadblock_string)
        return False, "", ""
    if location_string + roadblock_string == lastrunstrings and need_ring == 1 and lastuser == uid:
        sentmsg = await msg.channel.send(embed=discord.Embed(color = ecolor, title="Map processed recently",
                                                             description=f"[Click here to nagivate to the previous run]({lastrunlink})"))
        return False, "", ""    
    if db_pro and need_ring != 0:
        await msg.channel.send("Please wait for a while, a date board is already in progress.")
        return False, "", ""
    if uid in cddict and need_ring != 0:
        rem_time = time.time() - cddict[uid]
        if rem_time < cd_pu:
            await msg.channel.send(f"Please wait `{stohr(cd_pu - round(rem_time))}` before requesting solution to another date board.")
            return False, "", ""
        else:
            cddict[uid] = time.time()
    else:
        cddict[uid] = time.time()
    lastrunstrings = location_string + roadblock_string
    lastuser = uid
    db_pro = True
    await msg.channel.send("Date Map received, processing...")
    locations = []
    for i in range(7):
        locations.append(list(location_string[i*5:(i+1)*5]))

    # Roadblocks has an extra row and column of "0" to help with "blocked" function
    roadblocks = []
    for i in range(13):
        if i % 2 == 0:
            roadblocks.append(list(roadblock_string[(i//2)*9:(i//2)*9+4]) + ["0"])
        else:
            roadblocks.append(list(roadblock_string[(i//2)*9+4:(i//2+1)*9]) + ["0"])
    roadblocks.append(list("0"*5))


    globalv = {
        "locations": locations,
        "roadblocks": roadblocks,
        "totalsol": 0,
        "bestsolution": {},
        "iterations": 0
    }
    await date(cur_turn, initial_resource, respawn_matrix, cur_row, cur_col, direction, [], globalv, need_ring)
    bestsolution = globalv["bestsolution"]

    deltatime = f"{math.floor(time.time() - starttime)}.{round(1000*(time.time() - starttime))%1000} s"

    solution = ""
    solutionemoji = ""
    report = f"Run duration: {deltatime}\n"
    report = report + f"Path explored: {globalv['iterations']}\nSolutions found: {globalv['totalsol']}\n"
    remainingresource = ""
    interpretedmap = ""


    for j in range(5):
        interpretedmap = interpretedmap + "------ "
    interpretedmap = interpretedmap + "\n"

    for i in range(len(roadblocks)-1):
        if i % 2 == 0:
            for j in range(4):
                interpretedmap = interpretedmap + f" {location_emojis[locations[i//2][j]]} "
                if roadblocks[i][j] == "0":
                    interpretedmap = interpretedmap + "|"
                else:
                    interpretedmap = interpretedmap + " "
            interpretedmap = interpretedmap + f" {location_emojis[locations[i // 2][4]]}\n"
        else:
            for j in range(5):
                if roadblocks[i][j] == "0":
                    interpretedmap = interpretedmap + "------"
                else:
                    interpretedmap = interpretedmap + "     "
                interpretedmap = interpretedmap + " "
            interpretedmap = interpretedmap + "\n"
    for j in range(5):
        interpretedmap = interpretedmap + "------ "
    interpretedmap = interpretedmap + "\n"

    if direction == "l":
        interpretedmap = interpretedmap + "     ⬅️ 🚘"
    else:
        interpretedmap = interpretedmap + "      🚘 ➡️"


    if bestsolution == {}:
        solution = "No solution found"
        remainingresource = "N/A"
        apearned = "N/A"
    else:
        report = report + f"Appearance of the best solution: path {bestsolution['iteration']}\n"

        for i in range(len(bestsolution["moves"])-1):
            solution = solution + denotations[bestsolution["moves"][i]] + ", "
            solutionemoji = solutionemoji + location_emojis[bestsolution["moves"][i]] + " "
        solution = solution + denotations[bestsolution["moves"][-1]]
        solutionemoji = solutionemoji + location_emojis[bestsolution["moves"][-1]] + " "

        apearned = math.ceil(sum(bestsolution["resources"][1:]) * len(bestsolution["moves"])/ 25 / 6)
        solutionemoji = solutionemoji #+ f"\n\nEstimated AP earned: {apearned}\n"

        report = report + "Ring acquired: " + str(bestsolution["ring"]) + "\n"
        report = report + "Shopping Mall acquired: " + str(bestsolution["shopping"]) + "\n"
        report = report + "Went home: " + str(bestsolution["home"]) + "\n"
        report = report + "Date successful: " + str(bestsolution["alive"]) + "\n"
        report = report + "Number of turns: " + str(len(bestsolution["moves"])) + "\n"

        remainingresource = "⛽ Gas: " + str(bestsolution["resources"][0]) + "\n"
        remainingresource = remainingresource + "🍔 Food: " + str(bestsolution["resources"][1]) + "\n"
        remainingresource = remainingresource + "🍹 Drink: " + str(bestsolution["resources"][2]) + "\n"
        remainingresource = remainingresource + "😌 Entertainment : " + str(bestsolution["resources"][3]) + "\n"

    poterror = []
    for i in locationlist[:-3]:
        if not i in location_string:
            poterror.append(denotations[i])

    if poterror:
        desc = "Please double check before you move, and report any errors to our support server.(Use `m.support`)\n"
        rvembed = discord.Embed(title="Date Solver", description=desc , colour = ecolor)
        rvembed.add_field(name="Error:", value=f"Missing: {', '.join(poterror)}", inline=False)
    else:
        desc = ""
        rvembed = discord.Embed(title="Date Solver", description="````"+solution+"````"+" "+"+"+" "+str(apearned)+" "+"AP", colour = ecolor)
        #rvembed.add_field(name="Emoji Path ", value = "⠀"+solutionemoji, inline=False)
        #rvembed.add_field(name="Estimated AP earned: ", value = str(apearned), inline=False)
        #rvembed.add_field(name="Solution:", value=solution + "\n" + solutionemoji, inline=False)
        #rvembed.add_field(name="Remaining Resource:", value=remainingresource, inline=False)
        rvembed.add_field(name="Report:", value=report, inline=False)
    #rvembed.add_field(name="Interpreted Map:", value=interpretedmap, inline=False)
    #rvembed.set_footer(text="React ➕ for more details.")
    db_pro = False
    return True, rvembed, report


class datesolve(commands.Cog):
    def __init__(self,bot):
        self.client = bot
        self.ecolor = 0x00FFB7

    ## Discord ##


    async def check_role(self, message, uid):
        global enabled_roles
        #print(uid)
        try:
            member = await message.guild.fetch_member(uid)
        except Exception as e:
            return False

        permitted = False

        for role in enabled_roles:
            _role = message.guild.get_role(role)
            if _role in member.roles:
                permitted = True

        return permitted


    def checkm(self, myself, rct, msg):
        def innercheck(reaction, user):
            return not user.id == myself and str(reaction.emoji) == rct and reaction.message.id == msg
        return innercheck


    @commands.Cog.listener()
    async def on_message(self, message):
        global lastrunlink
        if message.channel.id not in enabled_channels:
            return
        imurl = ""
        uid = 0
        need_ring = 1
        kvi_cond = False
        if not message.embeds == []:
            if not message.embeds[0].image.url == discord.Embed.Empty:
                # karuta kvi
                try:
                    uid = int(message.embeds[0].description.split("@")[1].split(">")[0])
                except:
                    return
                imurl = message.embeds[0].image.url
                kvi_cond = True
            elif not message.embeds[0].url == discord.Embed.Empty:
                # link message
                uid = message.author.id
                imurl = message.embeds[0].url
        if kvi_cond:
            return
        if not kvi_cond and imurl == "" and message.attachments:
            imurl = message.attachments[0].url
            uid = message.author.id
        if not kvi_cond and imurl == "" and message.content.startswith("http") and message.content.endswith(".png"):
            imurl = message.content
        if not (imurl.startswith("http") and imurl.endswith(".png")):
            return
        if len(imurl) <= 0:
            return
        if message.channel.id == 874183195409674290 and not kvi_cond:
            return
        if not kvi_cond and not await self.check_role(message, uid):
            return
        memn = uid
        try:
            memn = await message.guild.fetch_member(uid)
            memn = str(memn)
        except:
            memn = str(uid)
            pass
        run_success, sendembed, report = await rundate(imurl, message, need_ring, uid)

        if run_success:
            sendembed.set_footer(text = f"{'React below to get route without ring | ' if 'ring' in sendembed.description else ''}Requested by : {memn}")
            sentmsg = await message.reply(embed=sendembed)
            lastrunlink = sentmsg.jump_url
            if "ring" in sendembed.description:
                await sentmsg.add_reaction("noring:873958263752900658")
                try:
                    rct, usr = await self.client.wait_for("reaction_add", check=self.checkm(self.client.user.id, "<:noring:873958263752900658>", sentmsg.id), timeout=20)
                except Exception as e:
                    # timeout
                    return
                run_success, sendembed, report = await rundate(imurl, message, 0, uid)
                if not run_success:
                    return
                sendembed.set_footer(text = f"Requested by : {memn}")
                sentmsg = await message.reply(embed=sendembed)
                lastrunlink = sentmsg.jump_url
            else:
                return
        else:
            return
    @command(name="$clear-queue", aliases=["$cq"])
    @commands.is_owner()
    async def clrqueue(self, ctx):
        global db_pro
        db_pro = False
        await ctx.channel.send("Queue cleared successfully.")
        return
def setup_date(bot):
    bot.add_cog(datesolve(bot))
