import asyncio
import os
import sys
import discord
from discord.ext import  commands
from discord import FFmpegPCMAudio
from help_cog import help_cog
from music_cog import music_cog


import youtube_dl

import yt_dlp

ctxmain = ["nothing"]

TOKEN = 
intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix= '-', intents=intents)


#client = discord.Client(intents=intents)






#remove the default help command so that we can write out own
client.remove_command('help')

#register the class with the bot











async def main():
    await client.add_cog(help_cog(client))
    await client.add_cog(music_cog(client))
    await client.start(TOKEN)

asyncio.run(main())





#@client.event
#async def on_message(message):
 #   username = str(message.author).split('#')[0]
  #  user_message = str(message.content)
   # channel = str(message.channel.name)
    #print(username +": " + user_message + " ("+channel+")")


    #if message.author == client.user:
     #   return
    #if user_message.lower() == "hello":
     #   await message.channel.send("hello")
      #  return