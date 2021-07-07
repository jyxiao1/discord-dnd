# bot.py
import os

import discord
from dotenv import load_dotenv
import random

load_dotenv()
# TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    try:
        msg = message.content
        msg = msg.lower()
        if msg.startswith('!jeff'):
            msgList = msg.split()
            if len(msgList) == 2:
                if msgList[1] == "owo":
                    await message.channel.send("https://www.youtube.com/watch?v=h6DNdop6pD8")

                if msgList[1] == "help":
                    await message.channel.send("Send two numbers as the minimum and maximum bounds for a random number generator, for example:"
                                               "\n !jeff 1 100")

                if msgList[1] == "lie":
                    await message.channel.send("I am pizi's totally real and not suspicious boyfriend")
                else:
                    ran = random.randint(0, int(msgList[1]))
                    returnMessage = "Your random number is " + str(ran) + " as divined by an incredibly smart and handsome programmer."
                    await message.channel.send(returnMessage)

            if len(msgList) == 3:
                ran = random.randint(int(msgList[1]), int(msgList[2]))
                returnMessage = "Your random number is " + str(ran) + " as divined by an incredibly smart and handsome programmer."
                await message.channel.send(returnMessage)
    except:
        return

client.run("ODYxNDI0MDcyNzkyMjExNDk2.YOJlrw.CMKc9GsJTi_HR4sQa7OsfGdxoAs")
