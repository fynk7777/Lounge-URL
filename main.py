import os
import re
from datetime import datetime, timedelta

import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands

from keep_alive import keep_alive


TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='lu.', intents=intents)
bot.owner_ids = [1212687868603007067, 987965367106293760]


def time_format(time: str) -> str:
    time = time[:23] + "Z"
    utc = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fZ")
    jst = utc + timedelta(hours=9)
    return jst.strftime("%Y/%m/%d %H:%M:%S")


def parse(id: int) -> dict[str, int | datetime | str]:
    res = requests.get(f'https://www.mk8dx-lounge.com/TableDetails/{str(id)}')
    soup = BeautifulSoup(res.text, 'html.parser')
    main = soup.find('main')
    data = main.findChildren()[0].findChildren()[0].findChildren()
    results = {
        "id": id,
        "created": time_format(data[3].findChildren()[0].get('data-time')),
        "verified": time_format(data[6].findChildren()[0].get('data-time')),
        "format": data[9].text.strip(),
        "tier": data[11].text.strip()
    }
    return results


@bot.event
async def on_ready():
    await bot.load_extension('jishaku')
    print(f"Logged in as {bot.user.name}")
    c = await bot.fetch_channel(1245028296417349656)
    e = discord.Embed(title="updated!", description=f"extensions: {bot.extensions}")
    await c.send(embed=e)


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    match = re.search(r'https://www\.mk8dx-lounge\.com/TableDetails/(\d+)', message.content)
    if match:
        id = match.group(1)
        data = parse(int(id))
        embed = discord.Embed(
            title=f"MK8DX Lounge",
            color=0x00ff00
        )
        embed.add_field(name="Table ID", value=data["id"])
        embed.add_field(name="Created", value=data["created"])
        embed.add_field(name="Verified", value=data["verified"])
        embed.add_field(name="Format", value=data["format"])
        embed.add_field(name="Tier", value=data["tier"])
        embed.set_image(url=f"https://www.mk8dx-lounge.com/TableImage/{id}.png")
        await message.reply(embed=embed)


# Discordボットの起動とHTTPサーバーの起動
try:
    keep_alive()
    bot.run(TOKEN)
except Exception as e:
    print(f'エラーが発生しました: {e}')
