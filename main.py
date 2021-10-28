# bot.py
import os

import discord
from dotenv import load_dotenv
import random
import echo_bot
from discord.ext import commands
load_dotenv()
# TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
jeffbot = echo_bot.Jeffbot(client=client)

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    try:
        if message.content.lower() == "kill it with fire":
            with open('tenor.gif', 'rb') as f:
                picture = discord.File(f)
                # embed = discord.Embed(
                #     # title='Title',
                #     description=reply,
                #     color=discord.Color.blurple())
                await message.channel.send(file=picture)

        if message.content.lower() == "thank you jeffbot":
            embed = discord.Embed(
                title='An Incredibly Handsome and Talented Programmer',
                description="You're very much welcome, *m'lady*",
                color=discord.Color.blurple()
            )
            with open('mlady.gif', 'rb') as f:
                picture = discord.File(f)
                # embed.set_image(url='mlady.gif')
                await message.channel.send(embed=embed, file=picture)

        reply = jeffbot.parse_message(message.content)
        if reply != "":
            embed = discord.Embed(
                # title='Title',
                description=reply,
                color=discord.Color.blurple()
            )
            # message = discord.Message
            # message.
            # embed.set_footer(text='This is a footer')
            await message.channel.send(embed = embed)
        # msg = message.content
        # msg = msg.lower()
        # if msg.startswith('!jeff'):
        #     msgList = msg.split()
        #     if len(msgList) == 2:
        #         if msgList[1] == "owo":
        #             await message.channel.send("https://www.youtube.com/watch?v=h6DNdop6pD8")
        #
        #         if msgList[1] == "help":
        #             await message.channel.send("Send two numbers as the minimum and maximum bounds for a random number generator, for example:"
        #                                        "\n !jeff 1 100")
        #
        #         if msgList[1] == "lie":
        #             await message.channel.send("I am pizi's totally real and not suspicious boyfriend")
        #
        #         else:
        #             ran = random.randint(0, int(msgList[1]))
        #             returnMessage = "Your random number is " + str(ran) + " as divined by an incredibly smart and handsome programmer."
        #             await message.channel.send(returnMessage)
        #
        #     if len(msgList) == 3:
        #         ran = random.randint(int(msgList[1]), int(msgList[2]))
        #         returnMessage = "Your random number is " + str(ran) + " as divined by an incredibly smart and handsome programmer."
        #         await message.channel.send(returnMessage)
    except:
        return

# @client.command
# async def displayembed():
#     embed = discord.Embed(
#         title = 'Title',
#         description = 'Description',
#         color = discord.Color.blurple()
#     )
#
#     embed.set_footer(text='This is a footer')


client.run("ODYxNDI0MDcyNzkyMjExNDk2.YOJlrw.CMKc9GsJTi_HR4sQa7OsfGdxoAs")
