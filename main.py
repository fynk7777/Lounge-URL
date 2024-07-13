import os
import re
import aiohttp
from datetime import datetime, timedelta
from keep_alive import keep_alive
import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

# Intentsの設定
intents = discord.Intents.default()
intents.dm_messages = True  # DMメッセージを受信するための設定
intents.messages = True      # サーバーでのメッセージを受信するための設定
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

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
    print(f"Logged in as {bot.user.name}")


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


bot.run(TOKEN)
