
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

wldict = {
    "My Teen Romantic Comedy SNAFU": {
        "Yukino Yukinoshita": 925775075783901236,
        "Yui Yuigahama": 925775130850889768
    },
    "Naruto Shippuden": {
        "Madara Uchiha": 925775075783901236,
        "Minato Namikaze": 925775130850889768,
        "Pain": 925775130850889768,
        "Obito Uchiha": 925775130850889768
    },
    "Attack on Titan": {
        "Mikasa Ackerman": 925774996155007026,
        "Eren Jaeger": 925774996155007026,
        "Armin Arlert": 925775075783901236,
        "Sasha Braus": 925775130850889768,
        "Erwin Smith": 925775130850889768,
        "Annie Leonhart": 925775130850889768,
        "Levi": 925774996155007026,
        "Hange Zoë": 925775075783901236,
        "Jean Kirschtein": 925775130850889768
    },
    "Arcane": {
        "Jayce": 925775130850889768,
        "Jinx": 925774996155007026,
        "Caitlyn": 925775033622724618,
        "Ekko": 925775075783901236,
        "Vi": 925775033622724618,
        "Heimerdinger": 925775130850889768,
        "Silco": 925775130850889768
    },
    "Naruto": {
        "Naruto Uzumaki": 925774996155007026,
        "Itachi Uchiha": 925774996155007026,
        "Kakashi Hatake": 925775033622724618,
        "Gaara": 925775130850889768,
        "Sakura Haruno": 925775130850889768,
        "Sasuke Uchiha": 925775033622724618,
        "Hinata Hyuuga": 925775033622724618,
        "Tsunade": 925775130850889768,
        "Jiraiya": 925775130850889768,
        "Shikamaru Nara": 925775130850889768
    },
    "Black Butler": {
        "Sebastian Michaelis": 925775130850889768,
        "Ciel Phantomhive": 925775130850889768
    },
    "Jujutsu Kaisen": {
        "Gojo Satoru": 925774996155007026,
        "Maki Zenin": 925775075783901236,
        "Mahito": 925775130850889768,
        "Sukuna": 925774996155007026,
        "Aoi Todo": 925775130850889768,
        "Megumi Fushiguro": 925774996155007026,
        "Yuji Itadori": 925774996155007026,
        "Kasumi Miwa": 925775130850889768,
        "Suguru Getou": 925775130850889768,
        "Nobara Kugisaki": 925775033622724618,
        "Toge Inumaki": 925775033622724618,
        "Panda": 925775130850889768,
        "Kento Nanami": 925775075783901236,
        "Yuta Okkotsu": 925775130850889768
    },
    "Horimiya": {
        "Izumi Miyamura": 925775033622724618,
        "Kyouko Hori": 925775033622724618
    },
    "Tokyo Ghoul": {
        "Juuzou Suzuya": 925775130850889768,
        "Ken Kaneki": 925774996155007026,
        "Touka Kirishima": 925775130850889768
    },
    "JoJo's Bizarre Adventure: Stardust Crusaders": {
        "Noriaki Kakyoin": 925775130850889768,
        "Jotaro Kujo": 925775033622724618
    },
    "Overflow": {
        "Ayane Shirakawa": 925775075783901236,
        "Kotone Shirakawa": 925775130850889768
    },
    "Food Wars! Shokugeki no Souma": {
        "Erina Nakiri": 925775130850889768,
        "Souma Yukihira": 925775130850889768
    },
    "Charlotte": {
        "Nao Tomori": 925775130850889768
    },
    "Sword Art Online": {
        "Asuna": 925775033622724618,
        "Kirito": 925775033622724618
    },
    "Dragon Ball Z": {
        "Goku": 925775033622724618,
        "Vegeta": 925775130850889768
    },
    "Rascal Does Not Dream of Bunny Girl Senpai": {
        "Rio Futaba": 925775075783901236,
        "Mai Sakurajima": 925774996155007026,
        "Sakuta Azusagawa": 925775130850889768,
        "Kaede Azusagawa": 925775130850889768
    },
    "Steins;Gate": {
        "Kurisu Makise": 925775075783901236,
        "Rintaro Okabe": 925775130850889768
    },
    "Solo Leveling": {
        "Sung Jin-Woo": 925774996155007026,
        "Cha Hae-In": 925775033622724618,
        "Igris": 925775130850889768,
        "Beru": 925775130850889768
    },
    "Future Diary": {
        "Yuno Gasai": 925775075783901236
    },
    "Akame ga Kill!": {
        "Akame": 925775075783901236,
        "Esdeath": 925775033622724618,
        "Mine": 925775130850889768
    },
    "Kakegurui": {
        "Yumeko Jabami": 925774996155007026,
        "Kirari Momobami": 925775130850889768,
        "Ririka Momobami": 925775130850889768,
        "Runa Yomozuki": 925775130850889768,
        "Mary Saotome": 925775130850889768
    },
    "High School DxD": {
        "Akeno Himejima": 925775033622724618,
        "Rias Gremory": 925774996155007026,
        "Koneko Toujou": 925775130850889768
    },
    "Hololive EN": {
        "Mori Calliope": 925775033622724618,
        "Gawr Gura": 925774996155007026,
        "Nanashi Mumei": 925775130850889768,
        "Watson Amelia": 925775075783901236,
        "Ouro Kronii": 925775130850889768,
        "Ninomae Ina'nis": 925775075783901236,
        "Takanashi Kiara": 925775130850889768
    },
    "My Hero Academia": {
        "Denki Kaminari": 925775130850889768,
        "Katsuki Bakugou": 925775033622724618,
        "Izuku Midoriya": 925775033622724618,
        "Kyouka Jirou": 925775130850889768,
        "Shouto Todoroki": 925774996155007026,
        "Ochako Uraraka": 925775130850889768,
        "All Might": 925775130850889768,
        "Tomura Shigaraki": 925775130850889768,
        "Tsuyu Asui": 925775130850889768,
        "Eijirou Kirishima": 925775130850889768,
        "Momo Yaoyorozu": 925775130850889768,
        "Shouta Aizawa": 925775130850889768
    },
    "Bungou Stray Dogs": {
        "Osamu Dazai": 925775033622724618,
        "Chuuya Nakahara": 925775130850889768,
        "Atsushi Nakajima": 925775130850889768,
        "Ranpo Edogawa": 925775130850889768
    },
    "Honkai Impact 3rd": {
        "Herrscher of Sentience": 925775130850889768,
        "Herrscher of Thunder": 925775130850889768
    },
    "One-Punch Man": {
        "Genos": 925775130850889768,
        "Saitama": 925775033622724618,
        "Tatsumaki": 925775130850889768,
        "Fubuki": 925775130850889768
    },
    "One Piece": {
        "Yamato": 925775033622724618,
        "Tony Tony Chopper": 925775075783901236,
        "Zoro Roronoa": 925774996155007026,
        "Monkey D. Luffy": 925774996155007026,
        "Nico Robin": 925775033622724618,
        "Nami": 925775033622724618,
        "Boa Hancock": 925775130850889768,
        "Portgas D. Ace": 925775075783901236,
        "Trafalgar Law": 925775075783901236,
        "Shanks": 925775130850889768,
        "Brook": 925775130850889768,
        "Sanji": 925775075783901236,
        "Usopp": 925775130850889768
    },
    "Demon Slayer: Kimetsu no Yaiba": {
        "Giyuu Tomioka": 925774996155007026,
        "Nezuko Kamado": 925774996155007026,
        "Kyoujurou Rengoku": 925774996155007026,
        "Tanjirou Kamado": 925774996155007026,
        "Tengen Uzui": 925775130850889768,
        "Muzan Kibutsuji": 925775130850889768,
        "Inosuke Hashibira": 925774996155007026,
        "Mitsuri Kanroji": 925775033622724618,
        "Shinobu Kochou": 925774996155007026,
        "Zenitsu Agatsuma": 925774996155007026,
        "Gyoumei Himejima": 925775130850889768,
        "Obanai Iguro": 925775130850889768,
        "Kanao Tsuyuri": 925775075783901236,
        "Muichirou Tokitou": 925775075783901236,
        "Sanemi Shinazugawa": 925775130850889768,
        "Sabito": 925775130850889768
    },
    "Kanojo, Okarishimasu": {
        "Sumi Sakurasawa": 925775130850889768,
        "Chizuru Mizuhara": 925775033622724618,
        "Ruka Sarashina": 925775130850889768
    },
    "JoJo's Bizarre Adventure": {
        "Dio Brando": 925775033622724618,
        "Joseph Joestar": 925775075783901236,
        "Jonathan Joestar": 925775130850889768,
        "Robert E. O. Speedwagon": 925775130850889768
    },
    "Code Geass: Lelouch of the Rebellion": {
        "C.C.": 925775075783901236,
        "Lelouch Lamperouge": 925775075783901236
    },
    "Vivy: Fluorite Eye's Song": {
        "Vivy": 925775130850889768
    },
    "Genshin Impact": {
        "Baal": 925774996155007026,
        "Hu Tao": 925774996155007026,
        "Arataki Itto": 925775033622724618,
        "Venti": 925775033622724618,
        "Albedo": 925775075783901236,
        "Lumine": 925775130850889768,
        "Sangonomiya Kokomi": 925775075783901236,
        "Gorou": 925775130850889768,
        "Childe": 925775033622724618,
        "Xiao": 925774996155007026,
        "Yae Miko": 925775075783901236,
        "Thoma": 925775075783901236,
        "Scaramouche": 925775130850889768,
        "Zhongli": 925775033622724618,
        "Klee": 925775075783901236,
        "Beidou": 925775075783901236,
        "Sucrose": 925775130850889768,
        "Ganyu": 925775033622724618,
        "Kaedehara Kazuha": 925774996155007026,
        "Keqing": 925775033622724618,
        "Qiqi": 925775130850889768,
        "Eula": 925775033622724618,
        "Chongyun": 925775130850889768,
        "Diluc": 925775033622724618,
        "Paimon": 925775075783901236,
        "Yoimiya": 925775075783901236,
        "Sayu": 925775130850889768,
        "Yanfei": 925775075783901236,
        "Jean": 925775130850889768,
        "Aether": 925775130850889768,
        "Bennett": 925775130850889768,
        "Amber": 925775130850889768,
        "Ningguang": 925775130850889768,
        "Razor": 925775130850889768,
        "Noelle": 925775130850889768,
        "Lisa": 925775130850889768,
        "Diona": 925775130850889768,
        "Kaeya": 925775075783901236,
        "Kamisato Ayaka": 925775033622724618,
        "Mona": 925775130850889768,
        "Xingqiu": 925775130850889768,
        "Fischl": 925775130850889768,
        "Dainsleif": 925775130850889768
    },
    "Fullmetal Alchemist": {
        "Roy Mustang": 925775130850889768,
        "Edward Elric": 925775075783901236
    },
    "Record of Ragnarok": {
        "Adam": 925775130850889768
    },
    "DARLING in the FRANXX": {
        "Zero Two": 925774996155007026
    },
    "Tokyo Revengers": {
        "Emma Sano": 925775130850889768,
        "Ken Ryuguji": 925774996155007026,
        "Kazutora Hanemiya": 925775075783901236,
        "Hinata Tachibana": 925775075783901236,
        "Shuji Hanma": 925775130850889768,
        "Manjiro Sano": 925774996155007026,
        "Takemichi Hanagaki": 925775075783901236,
        "Chifuyu Matsuno": 925775033622724618,
        "Keisuke Baji": 925775033622724618,
        "Takashi Mitsuya": 925775075783901236,
        "Nahoya Kawata": 925775130850889768
    },
    "Toilet-Bound Hanako-kun": {
        "Hanako": 925775075783901236,
        "Nene Yashiro": 925775130850889768,
        "Sousuke Mitsuba": 925775130850889768
    },
    "Hunter x Hunter": {
        "Killua Zoldyck": 925774996155007026,
        "Chrollo Lucilfer": 925775130850889768,
        "Kurapika": 925775075783901236,
        "Shizuku": 925775130850889768,
        "Gon Freecss": 925775033622724618,
        "Hisoka": 925775033622724618,
        "Feitan": 925775130850889768
    },
    "Danganronpa: The Animation": {
        "Kyouko Kirigiri": 925775130850889768,
        "Junko Enoshima": 925775130850889768,
        "Celestia Ludenberg": 925775130850889768
    },
    "Bleach": {
        "Ichigo Kurosaki": 925775075783901236,
        "Sousuke Aizen": 925775130850889768,
        "Rukia Kuchiki": 925775130850889768,
        "Yoruichi Shihouin": 925775130850889768,
        "Kisuke Urahara": 925775130850889768
    },
    "Classroom of the Elite": {
        "Suzune Horikita": 925775130850889768,
        "Kiyotaka Ayanokouji": 925775130850889768
    },
    "Highschool of the Dead": {
        "Saeko Busujima": 925775130850889768
    },
    "Pokémon: Black & White: Adventures in Unova": {
        "James's Amoonguss": 925775130850889768
    },
    "SK8 the Infinity": {
        "Reki Kyan": 925775075783901236,
        "Langa Hasegawa": 925775075783901236,
        "Kaoru Sakurayashiki": 925775130850889768,
        "Miya Chinen": 925775130850889768
    },
    "Haikyuu!!": {
        "Tobio Kageyama": 925775075783901236,
        "Kenma Kozume": 925775075783901236,
        "Tetsurou Kuroo": 925775130850889768,
        "Tooru Oikawa": 925775075783901236,
        "Shoyo Hinata": 925775033622724618,
        "Yu Nishinoya": 925775130850889768
    },
    "High-Rise Invasion": {
        "Sniper Mask": 925775075783901236
    },
    "Domestic Girlfriend": {
        "Rui Tachibana": 925775130850889768
    },
    "Tsukimichi: Moonlit Fantasy": {
        "Mio": 925775130850889768,
        "Tomoe": 925775130850889768
    },
    "The Seven Deadly Sins: Signs of Holy War": {
        "Escanor": 925775130850889768
    },
    "Danganronpa 2: Goodbye Despair": {
        "Mikan Tsumiki": 925775130850889768,
        "Nagito Komaeda": 925775075783901236,
        "Ibuki Mioda": 925775130850889768
    },
    "takt op.Destiny": {
        "Destiny": 925775033622724618,
        "Cosette Schneider": 925775130850889768,
        "Titan": 925775130850889768,
        "Takt Asahina": 925775075783901236
    },
    "Overlord": {
        "Albedo": 925775075783901236,
        "Momonga": 925775130850889768
    },
    "Don't Toy with Me, Miss Nagatoro": {
        "Hayase Nagatoro": 925775033622724618
    },
    "That Time I Got Reincarnated as a Slime": {
        "Rimuru Tempest": 925775033622724618,
        "Milim Nava": 925775130850889768
    },
    "My Hero Academia 2": {
        "Dabi": 925775075783901236,
        "Himiko Toga": 925775033622724618
    },
    "The Quintessential Quintuplets": {
        "Ichika Nakano": 925775130850889768,
        "Miku Nakano": 925774996155007026,
        "Nino Nakano": 925775033622724618,
        "Yotsuba Nakano": 925775075783901236
    },
    "Redo of Healer": {
        "Setsuna": 925775130850889768,
        "Flare Arlgrande Jioral": 925775130850889768
    },
    "Fate/Apocrypha": {
        "Astolfo": 925775075783901236
    },
    "Hyouka": {
        "Houtarou Oreki": 925775130850889768
    },
    "Wandering Witch: The Journey of Elaina": {
        "Elaina": 925775130850889768
    },
    "Doki Doki Literature Club!": {
        "Yuri": 925775130850889768,
        "Natsuki": 925775130850889768,
        "Sayori": 925775130850889768
    },
    "To Your Eternity": {
        "Fushi": 925775075783901236
    },
    "Black Clover": {
        "Asta": 925775033622724618,
        "Noelle Silva": 925775130850889768,
        "Yami Sukehiro": 925775075783901236,
        "Secre Swallowtail": 925775130850889768,
        "Yuno": 925775130850889768
    },
    "The Seven Deadly Sins": {
        "Meliodas": 925775075783901236,
        "Ban": 925775130850889768
    },
    "Fate/stay night": {
        "Saber": 925775033622724618,
        "Rin Tohsaka": 925775033622724618,
        "Gilgamesh": 925775130850889768
    },
    "Maou Gakuin no Futekigousha": {
        "Anos Voldigoad": 925775130850889768
    },
    "KonoSuba: God's blessing on this wonderful world!": {
        "Kazuma Satou": 925775130850889768,
        "Aqua": 925775075783901236,
        "Megumin": 925775033622724618
    },
    "JoJo's Bizarre Adventure: Steel Ball Run": {
        "Gyro Zeppeli": 925775075783901236,
        "Johnny Joestar": 925775075783901236,
        "Funny Valentine": 925775130850889768,
        "Diego Brando": 925775130850889768
    },
    "JoJo's Bizarre Adventure: Stone Ocean": {
        "Jolyne Cujoh": 925775033622724618,
        "Ermes Costello": 925775130850889768,
        "Enrico Pucci": 925775130850889768,
        "F.F.": 925775130850889768,
        "Weather Report": 925775130850889768
    },
    "Kaguya-sama: Love Is War": {
        "Ai Hayasaka": 925775075783901236,
        "Chika Fujiwara": 925775033622724618,
        "Yu Ishigami": 925775130850889768,
        "Kaguya Shinomiya": 925775033622724618
    },
    "The Pet Girl of Sakurasou": {
        "Mashiro Shiina": 925775130850889768
    },
    "Neon Genesis Evangelion": {
        "Asuka Langley Soryu": 925775075783901236,
        "Shinji Ikari": 925775130850889768,
        "Rei Ayanami": 925775075783901236,
        "Misato Katsuragi": 925775130850889768
    },
    "Plastic Memories": {
        "Isla": 925775130850889768
    },
    "Guilty Crown": {
        "Inori Yuzuriha": 925775130850889768
    },
    "Seraph of the End: Battle in Nagoya": {
        "Shinoa Hiiragi": 925775130850889768,
        "Krul Tepes": 925775130850889768,
        "Mikaela Hyakuya": 925775130850889768
    },
    "Is It Wrong to Try to Pick Up Girls in a Dungeon?": {
        "Hestia": 925775130850889768
    },
    "Hellsing": {
        "Alucard": 925775130850889768
    },
    "The Detective is Already Dead": {
        "Siesta": 925775033622724618
    },
    "Hunter x Hunter (2011)": {
        "Meruem": 925775130850889768
    },
    "My Hero Academia 4": {
        "Eri": 925775130850889768,
        "Hawks": 925775130850889768
    },
    "Sword Art Online: Alicization": {
        "Alice Synthesis Thirty": 925775130850889768
    },
    "JoJo's Bizarre Adventure: Diamond Is Unbreakable": {
        "Yoshikage Kira": 925775130850889768,
        "Josuke Higashikata": 925775130850889768
    },
    "Wonder Egg Priority": {
        "Ai Ooto": 925775075783901236,
        "Rika Kawai": 925775130850889768
    },
    "InuYasha": {
        "Inuyasha": 925775130850889768
    },
    "Hololive: Holo no Graffiti": {
        "Kiryu Coco": 925775130850889768,
        "Hoshimachi Suisei": 925775130850889768,
        "Shirakami Fubuki": 925775130850889768,
        "Inugami Korone": 925775130850889768,
        "Nekomata Okayu": 925775130850889768,
        "Uruha Rushia": 925775130850889768,
        "Usada Pekora": 925775130850889768,
        "Houshou Marine": 925775130850889768
    },
    "Mushoku Tensei: Jobless Reincarnation": {
        "Rudeus Greyrat": 925775130850889768,
        "Eris Boreas Greyrat": 925775075783901236,
        "Roxy Migurdia": 925775075783901236
    },
    "Mob Psycho 100": {
        "Shigeo Kageyama": 925775075783901236
    },
    "your name.": {
        "Mitsuha Miyamizu": 925775130850889768
    },
    "No Game No Life": {
        "Sora": 925775130850889768,
        "Jibril": 925775130850889768,
        "Shiro": 925775075783901236
    },
    "Violet Evergarden": {
        "Violet Evergarden": 925775033622724618
    },
    "Komi-san wa, Komyushou desu.": {
        "Shouko Komi": 925774996155007026
    },
    "Death Note": {
        "Ryuk": 925775130850889768,
        "L": 925775033622724618,
        "Light Yagami": 925775075783901236,
        "Misa Amane": 925775130850889768
    },
    "My Neighbor Totoro": {
        "Totoro": 925775130850889768
    },
    "Mo Dao Zu Shi": {
        "Wei Wuxian": 925775130850889768
    },
    "Obey Me!": {
        "Lucifer": 925775130850889768
    },
    "Chivalry of a Failed Knight": {
        "Stella Vermillion": 925775130850889768
    },
    "I Want to Eat Your Pancreas": {},
    "Tears of Themis": {
        "Artem Wing": 925775130850889768,
        "Marius von Hagen": 925775130850889768
    },
    "Attack on Titan: The Final Season": {
        "Pieck Finger": 925775075783901236
    },
    "Yarichin Bitch-bu": {
        "Ayato Yuri": 925775130850889768
    },
    "The Rising of the Shield Hero": {
        "Raphtalia": 925775075783901236,
        "Naofumi Iwatani": 925775130850889768
    },
    "JoJo's Bizarre Adventure: Golden Wind": {
        "Giorno Giovanna": 925775075783901236,
        "Bruno Bucciarati": 925775130850889768
    },
    "Itadaki! Seieki": {
        "Setagaya Mari": 925775130850889768
    },
    "The Case Study of Vanitas": {
        "Jeanne": 925775130850889768,
        "Vanitas": 925775033622724618,
        "Dominique de Sade": 925775130850889768,
        "Noé Archiviste": 925775130850889768
    },
    "Vinland Saga": {
        "Thorfinn Thordarson": 925775130850889768
    },
    "Miss Kobayashi's Dragon Maid": {
        "Kanna Kamui": 925775033622724618,
        "Tohru": 925775075783901236,
        "Lucoa": 925775130850889768
    },
    "Kirby: Right Back at Ya!": {
        "Kirby": 925775130850889768
    },
    "Love, Chunibyo & Other Delusions!": {
        "Rikka Takanashi": 925775075783901236
    },
    "Given": {
        "Mafuyu Sato": 925775130850889768
    },
    "Fire Force": {
        "Tamaki Kotatsu": 925775075783901236,
        "Shinra Kusakabe": 925775130850889768,
        "Benimaru Shinmon": 925775130850889768
    },
    "Howl's Moving Castle": {
        "Howl": 925775075783901236
    },
    "Persona 5 the Animation": {
        "Joker": 925775130850889768
    },
    "Assassination Classroom": {
        "Nagisa Shiota": 925775130850889768,
        "Karma Akabane": 925775075783901236,
        "Koro-sensei": 925775130850889768
    },
    "Spy x Family": {
        "Yor Forger": 925775075783901236,
        "Loid Forger": 925775130850889768
    },
    "Danganronpa V3: Killing Harmony": {
        "Miu Iruma": 925775130850889768,
        "Shuichi Saihara": 925775130850889768,
        "Kokichi Ouma": 925775130850889768
    },
    "Tower of God": {
        "Khun Aguero Agnis": 925775130850889768,
        "Twenty-Fifth Baam": 925775130850889768
    },
    "Date a Live": {
        "Kurumi Tokisaki": 925775033622724618
    },
    "Fairy Tail": {
        "Gray Fullbuster": 925775130850889768,
        "Lucy Heartfilia": 925775130850889768,
        "Natsu Dragneel": 925775075783901236,
        "Erza Scarlet": 925775075783901236
    },
    "Gintama": {
        "Gintoki Sakata": 925775130850889768
    },
    "Dragon Ball Super": {
        "Goku Black": 925775130850889768
    },
    "Mankitsu Happening": {
        "Rei Suzukawa": 925775130850889768
    },
    "Berserk": {},
    "Miss Kobayashi's Dragon Maid S": {
        "Ilulu": 925775130850889768
    },
    "Re:ZERO -Starting Life in Another World-": {
        "Rem": 925774996155007026,
        "Ram": 925775075783901236,
        "Emilia": 925775033622724618,
        "Subaru Natsuki": 925775130850889768,
        "Ferris": 925775130850889768
    },
    "Demon Slayer: Kimetsu no Yaiba the Movie: Mugen Train": {
        "Akaza": 925775075783901236
    },
    "Boku no Pico": {
        "Pico": 925775130850889768
    },
    "Nisekoi": {
        "Chitoge Kirisaki": 925775130850889768
    },
    "Blue Exorcist": {
        "Rin Okumura": 925775130850889768
    },
    "Fruits Basket": {
        "Tohru Honda": 925775130850889768,
        "Kyo Sohma": 925775130850889768
    },
    "Bakemonogatari": {
        "Shinobu Oshino": 925775130850889768,
        "Hitagi Senjogahara": 925775130850889768
    },
    "Haikyuu!! Second Season": {
        "Koutarou Bokuto": 925775075783901236,
        "Keiji Akaashi": 925775130850889768
    },
    "The Way of the Househusband": {
        "Tatsu": 925775130850889768
    },
    "Toradora!": {
        "Taiga Aisaka": 925775075783901236
    },
    "Pingu in the City": {
        "Pingu": 925775130850889768
    },
    "K-On!": {
        "Mio Akiyama": 925775130850889768,
        "Yui Hirasawa": 925775130850889768
    },
    "Sailor Moon": {
        "Sailor Moon": 925775130850889768
    },
    "Soul Eater": {
        "Death the Kid": 925775130850889768
    },
    "Hatsune Miku: Downloader": {
        "Miku Hatsune": 925775130850889768
    },
    "Kuroko's Basketball": {
        "Tetsuya Kuroko": 925775130850889768
    },
    "JoJo's Bizarre Adventure: JoJolion": {
        "Josuke Higashikata": 925775130850889768
    },
    "Ouran High School Host Club": {
        "Tamaki Suoh": 925775130850889768
    },
    "Beastars": {
        "Legosi": 925775130850889768
    },
    "Dororo": {
        "Hyakkimaru": 925775130850889768
    },
    "Monogatari Series: Second Season": {
        "Kiss-Shot": 925775130850889768
    },
    "Kamisama Kiss": {
        "Tomoe": 925775130850889768
    },
    "Your lie in April": {
        "Kaori Miyazono": 925775075783901236
    },
    "Re:ZERO -Starting Life in Another World- Season 2": {
        "Echidna": 925775130850889768
    },
    "Boruto: Naruto the Movie": {
        "Boruto Uzumaki": 925775130850889768
    },
    "The Helpful Fox Senko-san": {
        "Senko": 925775130850889768
    },
    "Higehiro: After Being Rejected, I Shaved and Took in a High School Runaway": {
        "Sayu Ogiwara": 925775075783901236
    },
    "A Silent Voice": {
        "Shouko Nishimiya": 925775075783901236,
        "Shouya Ishida": 925775130850889768
    },
    "Cowboy Bebop": {
        "Spike Spiegel": 925775130850889768
    },
    "Banana Fish": {
        "Ash Lynx": 925775130850889768
    },
    "Flying House": {
        "Jesus Christ": 925775130850889768
    },
    "Yuri!!! on Ice": {
        "Victor Nikiforov": 925775130850889768
    },
    "Sword Art Online II": {
        "Sinon": 925775130850889768
    },
    "86 EIGHTY-SIX": {
        "Vladilena Milizé": 925775075783901236
    },
    "Fugou Keiji: Balance:Unlimited": {
        "Kanbe Daisuke": 925775130850889768
    },
    "Black Lagoon": {
        "Revy": 925775130850889768
    },
    "Spirited Away": {
        "Haku": 925775130850889768
    },
    "Fate/Grand Order": {
        "Ishtar": 925775130850889768,
        "Jeanne d'Arc (Alter)": 925775130850889768
    },
    "Pokémon": {
        "Pikachu": 925775130850889768
    },
    "The God of High School": {
        "Jin Mori": 925775130850889768
    },
    "A Certain Scientific Railgun": {
        "Misaka Mikoto": 925775130850889768
    },
    "Youjo Senki: Saga of Tanya the Evil": {
        "Tanya Degurechaff": 925775130850889768
    },
    "Dr. Stone": {
        "Senkuu": 925775075783901236
    },
    "Himouto! Umaru-chan": {
        "Umaru Doma": 925775130850889768
    },
    "The Disastrous Life of Saiki K.": {
        "Kusuo Saiki": 925775075783901236,
        "Shun Kaidou": 925775130850889768
    },
    "Kaichou wa Maid-sama!": {
        "Takumi Usui": 925775130850889768
    },
    "Tonikaku Kawaii": {
        "Tsukasa Yuzaki": 925775075783901236
    },
    "So I'm a Spider, So What?": {
        "Kumoko": 925775130850889768
    },
    "Oshi no Ko": {
        "Ai Hoshino": 925775130850889768
    },
    "The Promised Neverland": {
        "Ray": 925775130850889768,
        "Emma": 925775130850889768,
        "Norman": 925775130850889768
    },
    "Beyond the Boundary": {
        "Mirai Kuriyama": 925775130850889768
    },
    "Dragon Ball Z Movie 12: Fusion Reborn": {
        "Gogeta": 925775130850889768
    },
    "NieR: Automata": {
        "2B": 925775075783901236
    },
    "Ane Naru Mono": {
        "Chiyo": 925775130850889768
    },
    "Noragami": {
        "Yato": 925775075783901236
    },
    "Kill La Kill": {
        "Ryuuko Matoi": 925775130850889768
    }
}

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
