# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 12:02:40 2020

@author: Alhasad K
"""
import asyncio
import base64
import datetime
import json
import os
import random
import re
import time
from urllib import parse, request

import discord
import nest_asyncio
import praw
import requests
from discord.ext import commands, tasks
from dotenv import load_dotenv

nest_asyncio.apply()

SERVER_ICON_URL = "https://cdn.discordapp.com/icons/729144885399257142/e474a43de34943c0523927ca9556b081.png?size=1024"

COMMANDS = ["!bb", "!youtube", "!clan", "!channel"]

ERRORS = ["Oops, that doesn't look like a brawlball room.\nEso no parece un lobby o.O"]

COOL_TITLES_ENG = [
    "Brawlball Time!",
    "You know what time it is.",
    "Time to play!",
    "Let's play!",
    "Get over here! (With Scorpion's voice)",
    "It's time..."
]

COOL_TITLES_ESP = [
    "¡Hora de Brawlball!",
    "Ya sabes qué hora es.",
    "¡A jugar pues!",
    "¡Juguemos!",
    "¡Ven para acá!",
    "Es hora..."
]

COOL_MESSAGES_ENG = [
    "That's my secret Cap. I'm always playing.",
    "Join us!",
    "My name is C3P0 and I am fluent in over 6 million forms of scoring.",
    "Come play with us! May the Brawlball Force be with you.",
    "Whosoever joins this room, if he be worthy, shall possess the power of Brawlball.",
    "Now is no time to mourn. Now is time for brawlball.",
    "What if I told you that Brawlhalla was now under the control of a dark lord of Brawlball?"
]

COOL_MESSAGES_ESP = [
    "Ese es mi secreto Cap. Siempre estoy jugando.",
    "¡Únetenos!",
    "Mi nombre es C3P0 y hablo con fluidez más de 6 millones de formas de hacer goles.",
    "Ven y juega con nosotros! Qué la Fuerza de Brawlball te acompañe.",
    "Quien se una a esta sala, si es digno, poseerá el poder de Brawlball.",
    "Ahora no es momento de lamentarse. Ahora es tiempo de Brawlball.",
    "¿Y si te dijera que Brawlhalla está ahora bajo el control de un señor oscuro de Brawlball?"
]

def select_cool(msg_or_title: str) -> tuple:
    if msg_or_title == "title":
        i = random.randint(0, len(COOL_TITLES_ENG)-1)
        return COOL_TITLES_ENG[i], COOL_TITLES_ESP[i]
    elif msg_or_title == "msg":
        i = random.randint(0, len(COOL_MESSAGES_ENG)-1)
        return COOL_MESSAGES_ENG[i], COOL_MESSAGES_ESP[i]
    else:
        raise Exception("** Invalid use!!")

def is_command(message: str) -> bool:
    for command in COMMANDS:
        if message.content.startswith(command):
            return True
    
    return False

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')
IMGUR_CLIENT_ID = os.getenv('IMGUR_CLIENT_ID')
IMGUR_CLIENT_SECRET = os.getenv('IMGUR_CLIENT_SECRET')
IMGUR_ALBUM_ID = os.getenv('IMGUR_ALBUM_ID')
IMGUR_ALBUM_DELETEHASH = os.getenv('IMGUR_ALBUM_DELETEHASH')
IMGUR_ALBUM_URL = f"https://api.imgur.com/3/album/{IMGUR_ALBUM_ID}/images"

REDDIT_LIMIT = 200

with open("imgur.json", "r") as f:
    imgur_requests = json.load(f)

IMGUR_ACCESS_TOKEN = imgur_requests["access_token"]
IMGUR_REFRESH_TOKEN = imgur_requests["refresh_token"]
IMGUR_TOKEN_TYPE = imgur_requests["token_type"]

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)

    print(
        f'{bot.user.name} is connected to the following guild:\n\t'
        f'{guild.name}(id: {guild.id})'
    )

    # bot.loop.create_task(called_once_a_day())
    await called_once_a_day()

@bot.command(pass_context=True, name="bb", help="Creates a nice panel with the brawlball room.\nUsage: !bb <room number>\n\nCrea un panel lindo para mostrar un lobby de brawlball.\nUso: !bb <número del lobby>")
async def bb(ctx, brawlball_room: int):
    cool_title_eng, cool_title_esp = select_cool("title")
    cool_descr_eng, cool_descr_esp = select_cool("msg")

    try:
        author = str(ctx.message.author).split("#")[0]
    except:
        author = ctx.message.author

    avatar = ctx.message.author.avatar_url
    
    bb = discord.Embed(
        colour=discord.Colour.dark_blue(),
    )

    bb.set_thumbnail(url=SERVER_ICON_URL)
    bb.set_author(name=author, icon_url=avatar)
    bb.add_field(name=cool_title_eng, value=cool_descr_eng, inline=True)
    bb.add_field(name=cool_title_esp, value=cool_descr_esp, inline=False)
    bb.add_field(name="Room", value=str(brawlball_room), inline=False)

    print("[?] Creating embed...")
    await ctx.message.channel.purge(limit=1)
    await ctx.send(embed=bb)
    print("[?] Done")

@bot.event
async def on_message(message):
    channel = "-".join(str(message.channel).split("-")[1:])
    if channel == "brawlball-rooms" and not message.content.startswith("!bb ") and not message.content in ERRORS:
        if not message.embeds:
            print("[*] Deleting message: " + message.content)
            await message.channel.purge(limit=1)

    await bot.process_commands(message)

@bot.command(name="youtube", help="Makes a youtube search")
async def youtube(ctx, *, search: str):
    print("[?] Looking for " + search)
    query_string = parse.urlencode({'search_query': search})
    html_content = request.urlopen('http://www.youtube.com/results?' + query_string)
    search_results = re.compile(r"watch\?v=(\S{11})").findall(html_content.read().decode())
    # print("[?] Found " + str(search_results))
    # I will put just the first result, you can loop the response to show more results
    print("[?] First result: " + search_results[0])
    await ctx.send('https://www.youtube.com/watch?v=' + search_results[0])
    print("[?] Done")

@bot.command(name="clan", help="Prints server info")
async def clan(ctx):
    print("[?] Getting info...")
    embed = discord.Embed(
        title=f"{ctx.guild.name}", 
        description="So you want to know about me, huh?", 
        timestamp=datetime.datetime.utcnow(), 
        color=discord.Color.blue()
    )

    embed.add_field(name="Server created at", value=f"{ctx.guild.created_at}")
    embed.add_field(name="Server Owner", value=f"{ctx.guild.owner}")
    embed.add_field(name="Server Region", value=f"{ctx.guild.region}")
    embed.add_field(name="Server ID", value=f"{ctx.guild.id}")
    # embed.set_thumbnail(url=f"{ctx.guild.icon}")
    embed.set_thumbnail(url=SERVER_ICON_URL)

    await ctx.send(embed=embed)
    print("[?] Done")

@bot.command(name="channel", help="Rock n Goal Official Youtube Channel")
async def channel(ctx):
    print("[?] Looking for rock and goal official youtube channel")
    await ctx.send('https://www.youtube.com/channel/UCJME2x6mWEVrZ_jldFyQSBA')
    print("[?] Done")

def generate_new_access_token() -> int:
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
        }
    payload = {
            "refresh_token": IMGUR_REFRESH_TOKEN,
            "client_id": IMGUR_CLIENT_ID,
            "client_secret": IMGUR_CLIENT_SECRET,
            "grant_type": "refresh_token"
        }
    print("[?] Attempting to get a new access token with the refresh token... ", end="")
    r2 = requests.post("https://api.imgur.com/oauth2/token", data=payload, headers=headers)
    if r2.status_code == 200:
        print("Done")
        with open("imgur.json", "w") as f:
            json.dump(r2.json(), f)

        global IMGUR_ACCESS_TOKEN 
        IMGUR_ACCESS_TOKEN = r2.json()["access_token"] # Updates the access token
        return 0
    else:
        print("Failed")
        return -1

def get_existing_memes() -> dict:
    headers = {
        "Authorization": "Client-ID " + IMGUR_CLIENT_ID
        }
    print("[?] Requesting to get album (Memes) images... ", end="")
    r = requests.get(IMGUR_ALBUM_URL, headers=headers)
    if r.status_code == 200:
        print("Done")
        return r.json()['data']
    else:
        print("Failed")
        return None
    
def upload_meme_to_imgur(image_filename: str, description: str) -> list:
    headers = {
        "Authorization": "Bearer " + IMGUR_ACCESS_TOKEN
        }
    params = {
        "image": base64.b64encode(open(image_filename, 'rb').read()),
        "description": description
        }
    print("[?] Requesting to upload meme " + image_filename + " to imgur... ", end="")
    r = requests.post("https://api.imgur.com/3/image", headers=headers, data=params)
    if r.status_code == 200:
        print("Done")
        return r.json()['data']
    else:
        print("Failed")
        correct = generate_new_access_token() == 0
        if correct:
            print("[?] Attempting again...")
            headers = {
                "Authorization": "Bearer " + IMGUR_ACCESS_TOKEN
            }
            r = requests.post("https://api.imgur.com/3/image", headers=headers, data=params)
            if r.status_code == 200:
                print("Done")
                return r.json()['data']

        return None
    
async def update_imgur_album(image_info: dict) -> 0:
    headers = {
        "Authorization": "Bearer " + IMGUR_ACCESS_TOKEN
        }
    params = {
        "ids[]": image_info['id'].strip()
        }
    print("[?] Requesting to transfer meme " + image_info['id'] + " to imgur album... ", end="")
    await asyncio.sleep(0.5)
    r = requests.post(f"https://api.imgur.com/3/album/{IMGUR_ALBUM_DELETEHASH}/add", headers=headers, data=params)
    await asyncio.sleep(0.5)
    if r.status_code == 200:
        print("Done")
        return 0
    else:
        print("Failed")
        print("[*] Maybe the access token has expired.")
        correct = generate_new_access_token() == 0
        if correct:
            print("[?] Attempting again...")
            headers = {
                "Authorization": "Bearer " + IMGUR_ACCESS_TOKEN
            }
            await asyncio.sleep(0.5)
            r = requests.post(f"https://api.imgur.com/3/album/{IMGUR_ALBUM_DELETEHASH}/add", headers=headers, data=params)
            await asyncio.sleep(0.5)
            if r.status_code == 200:
                print("Done")
                return 0
            
        return -1

def get_new_memes():
    r = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    
    sub = r.subreddit("Brawlhalla")
    posts = sub.hot(limit=REDDIT_LIMIT)
    new_memes = []
    for i, p in enumerate(posts):
        try:
            url = str(p.url)
            if 'Meme' in p.link_flair_richtext[0].values():
                # Check if the link is an image
                if url.endswith("jpg") or url.endswith("png"):
                    # Retrieve the image and save it in current folder
                    print("[?] Downloading meme " + str(i) + ". " + clean_string(p.title))
                    print("\tFrom url: " + url)
                    request.urlretrieve(url, f"{str(p.ups)};;,{clean_string(p.title)}.{url[-3:]}")
                    new_memes.append(f"{str(p.ups)};;,{clean_string(p.title)}.{url[-3:]}")
        except:
            print("[*] Found some error with " + url + ". Continuing...")
            continue
    
    return new_memes

def remove_image_from_imgur(all_images: list, image_id: str) -> None:
    headers = {
        "Authorization": "Bearer " + IMGUR_ACCESS_TOKEN
        }

    params = {
        "ids[]": [image['id'] for image in all_images if image['id'] != image_id]
    }
    print("[?] Requesting to remove image " + image_id + " from imgur album... ", end="")
    r = requests.post(f"https://api.imgur.com/3/album/{IMGUR_ALBUM_ID}", headers=headers, data=params)
    if r.status_code == 200:
        print("Done")
        return 0
    else:
        print("Failed")
        print("[*] Maybe the access token has expired.")
        return -1

async def download_memes():    
    # Uploads new memes downloaded from reddit.
    existing_memes = get_existing_memes()
    if existing_memes is None:
        print("[*] Skipping entire function download_memes()")
        return

    existing_memes_names = [str(meme['description'].split(";;,")[1]) for meme in existing_memes]
    print("[?] Getting new memes from reddit...")
    new_memes = get_new_memes()
    print("[+] Done")
    if new_memes:
        print("[?] Getting rid of existing memes... ")
        filtered_new_memes = new_memes.copy()
        for i, new_meme in enumerate(new_memes):
            if new_meme.split(";;,")[1][:-4] in existing_memes_names or "(OLD)" + new_meme.split(";;,")[1][:-4] in existing_memes_names:
                print("[*] Found existing meme " + new_meme[:-4] + ". Deleting... ", end="")
                filtered_new_memes.remove(new_meme)
                print("Done")
        print("[+] Done")
        new_memes = filtered_new_memes
        if new_memes:
            print("[?] Uploading new memes to imgur... ")
            for new_meme in new_memes:
                print("[?] Current: " + new_meme)
                uploaded_meme_info = upload_meme_to_imgur(new_meme, new_meme[:-4])
                await update_imgur_album(uploaded_meme_info)
            print("[+] Done")

            print("[?] Cleaning file system... ")
            for new_meme in new_memes:
                print("[*] Deleting " + new_meme + " from current directory... ", end="")
                os.remove(new_meme)
                print("Done")
        else:
            print("[*] Looks like all memes have previously been added to imgur.")
    else:
        print("[*] No new memes found.")

    '''
        Gets full list of memes and returns the best one.
    '''
    print("[?] Waiting for API to update... ", end="")
    await asyncio.sleep(1200)
    print("Done")
    print("[+] Getting full list of memes...")
    complete_memes_list = get_existing_memes()
    print("[?] Getting best meme... ", end="")
    no_error = True
    best_meme = {"title": "", "link": "", "id": ""}
    most_ups = 0
    for meme in complete_memes_list:
        try:
            if meme['description'].split(";;,")[1].startswith("(OLD)"):
                continue
            ups = int(meme['description'].split(";;,")[0])
            if most_ups < ups:
                most_ups = ups
                best_meme['link'] = meme['link']
                best_meme['title'] = meme['description'].split(";;,")[1]
                best_meme['id'] = meme['id']
        except:
            print("")
            print("[*] Found some error while dealing with " + meme['title'] + " with link " + meme['link'])
            no_error = False
            continue

    if no_error:
        print("Done")
    
    print("[+] Found best meme: " + best_meme['title'])
    print("[+] Removing best meme from imgur, since it's going to be sent... ")
    remove_image_from_imgur(complete_memes_list, best_meme['id'])
    print("[?] Uploading best meme to imgur again, but with updated description (to avoid a future send)... ")
    url = best_meme['link']
    title = best_meme['title']
    file_ = f"meme_to_send.{url[-3:]}"
    request.urlretrieve(url, file_)
    uploaded_meme_info = upload_meme_to_imgur(file_, str(most_ups) + ";;,(OLD)" + title)
    await update_imgur_album(uploaded_meme_info)
    os.remove(file_)
    return best_meme
  
def clean_string(raw: str) -> str:
    if "u/" in raw:
        raw = raw.split("u/")[0]
    if '"' in raw:
        raw = raw.replace('"', "'")
    raw = de_emojify(raw)
    return raw.strip()

def de_emojify(text: str) -> str:
    regrex_pattern = re.compile(pattern = "["
                                            u"\U0001F600-\U0001F64F"  # emoticons
                                            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                            u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                          "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'', text)

async def send_meme(ctx, best_meme: dict) -> None:
    url = best_meme['link']
    title = best_meme['title']
    file_ = f"meme_to_send.{url[-3:]}"
    request.urlretrieve(url, file_)
    with open(file_, "rb") as fh:
        f = discord.File(fh, filename=file_)

    await ctx.send(title)
    await ctx.send(file=f)
    print("[+] Meme sent: " + title)
    os.remove(file_)

async def called_once_a_day():
    await bot.wait_until_ready()
    '''
    while True:
        print("[+] Finished waiting.")
        download_memes()
        message_channel = bot.get_channel(743284606031364177)
        print(f"[+] Got channel {message_channel}")
        await send_meme(message_channel)
        print("[?] Waiting to send next meme...")
        await asyncio.sleep(70000) # 1 day-ish
    '''
    print("[+] Going to send meme...")
    best_meme = await download_memes()
    message_channel = bot.get_channel(743284606031364177)
    print(f"[+] Got channel {message_channel}")
    await send_meme(message_channel, best_meme)

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    print("[*] Shutting down the bot...")
    await ctx.bot.logout()

bot.run(TOKEN)