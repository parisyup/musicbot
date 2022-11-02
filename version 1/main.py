import asyncio
import sys

import discord
from discord.ext import  commands
from discord import FFmpegPCMAudio


import youtube_dl
import os
import yt_dlp

ctxmain = ["nothing"]

TOKEN = 
intents = discord.Intents.default()
intents.message_content = True
#client = discord.Client(intents=intents)
client = commands.Bot(command_prefix= '-', intents=intents)

queues = {}
queues2 = []
queuesNames = []
queuesNames2 = []
nameOfSongsInQ = []
currentSong = []

msg1 = []
msg2 = []


ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}


def updateCurrentSong(x):
    currentSong.insert(0,x)

async def check_queue(ctx, id):
    currentSong.pop(0)
    await ctx.invoke(client.get_command('controlPanel'))
    if queues[id] != []:
        voice = ctx.guild.voice_client
        source = queues[id].pop(0)
        queues2.pop(0)
        updateCurrentSong(nameOfSongsInQ[0])
        nameOfSongsInQ.pop(0)
        player = voice.play(source, after=lambda x=None: check_queue(ctx, ctx.message.guild.id))
        songNumber = len(queuesNames2) - 1
        print("song" + str(songNumber) + ".mp3")
        for file in os.listdir("./"):
            if file.endswith("song" + str(songNumber) + ".mp3"):
                os.remove(file)
        queuesNames2.append(0)


@commands.Cog.listener()
async def on_voice_state_update(self, member, before, after):
    print("pp3")
    if not member.id == self.bot.user.id:
        return





@client.event
async def on_ready():
    print("ready! user: {0.user}".format(client))
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.remove(file)



@client.command()
async def hello(ctx):
    await ctx.send("Hi")



@client.command()
async def plshelp(ctx):
    await ctx.send("Most of the things are self explanatory so stop being a retard. read my description to see what is available.")

@client.command(pass_context = True , name = "join", aliases = ["j"])
async def join(ctx):
    if (ctx.voice_client):
        await ctx.send("I'M BUSY!")
        return
    if(ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        await ctx.send("Hello")
        await ctx.invoke(client.get_command('checkForLeave'))

    else:
        await ctx.send("dumbass... how the fuck can i join ur vc if u arent in one?")

@client.command(pass_context = True, name = "leave", aliases = ["l", "leaf"])
async def leave(ctx):
    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Bye bye... finally")
    else:
        await ctx.send("dumbass... how the fuck can i leave ur vc if im not in one?")

@client.command(pass_context = True, name = "pause", aliases = ["ps", "stop"])
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
        await ctx.send("Paused.")
    else:
        await ctx.send("dumbass... no audio is playing")






@client.command(pass_context = True, name = "resume", aliases = ["r", "continue"])
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
        await ctx.send("Resuming..")
    else:
        await ctx.send("dumbass... no audio is paused")


@client.command(pass_context = True, name = "skip", aliases = ["s", "skiping"])
async def skip(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()
    await ctx.send("Skipped")
    songNumber = len(queuesNames2) - 1
    for file in os.listdir("./"):
        if file.endswith("song" + str(songNumber) + ".mp3"):
            os.remove(file)


@client.command(pass_context = True, name = "skipto", aliases = ["sto", "skipTo", "st", "skips"])
async def skipto(ctx, arg):
    arg = int(arg)
    if len(nameOfSongsInQ) < arg-1:
        ctx.send("u cant skip to a song number that isnt in the -q... obviously ")
        return
    if str(arg).isdigit():
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        for x in range(arg):
            voice.stop()
        await ctx.send("skipped " + str(arg) + " songs.")
    else:
        await ctx.send("u are truly a dumbass pick a number from the list given by -q dont give me fkin " + str(arg))

@client.command(pass_context = True , name = "checkForLeave", help="checkForLeave")
async def checkForLeave(ctx):
    voice = ctx.channel.guild.voice_client
    time = 0
    while True:
        print(time)
        await asyncio.sleep(1)
        time = time + 1
        if voice.is_playing() and not voice.is_paused():
            time = 0
        if time == 90:
            await voice.disconnect()
            await ctx.send("Left due to inactivity restarting bot to ensure everything keeps working as intended. Give him a second :)")
            await ctx.invoke(client.get_command('restart'))
        if not voice.is_connected():
            break

@client.command(pass_context = True, name = "play", aliases = ["p"], help="please input the utube link")
async def play(ctx, arg):
    if "&list" in arg:
        arg = arg.split('&list')[0]

    if(not ctx.voice_client):
        if(ctx.author.voice):
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        else:
            await ctx.send("dumbass... how the fuck can i join ur vc if u arent in one?")
            return


    if "http" in arg:
        try:
            voice = ctx.guild.voice_client
            await ctx.send("adding song....")
            if voice.is_playing():
                counter = len(queuesNames)
                queuesNames.append(0)
                ydl = yt_dlp.YoutubeDL(ydl_opts)
                ydl.download(str(arg))
                for file in os.listdir("./"):
                    if file in queues2:
                        print("lol")
                    else:
                        if file.endswith(".mp3"):
                            nameOfSongsInQ.append(file.split('.mp3')[0])
                            os.rename(file, "song" + str(counter) + ".mp3")
                            queues2.append("song" + str(counter) + ".mp3")
                            arg = "song" + str(counter) + ".mp3"
                source = FFmpegPCMAudio(arg)

                guild_id = ctx.message.guild.id

                if guild_id in queues:
                    queues[guild_id].append(source)
                else:
                    queues[guild_id] = [source]

                await ctx.send("Added to q")
                await ctx.invoke(client.get_command('controlPanel'))
                await ctx.invoke(client.get_command('checkForLeave'))
                return

            counter = len(queuesNames)
            queuesNames.append(0)
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            ydl.download(arg)
            for file in os.listdir("./"):
                if file in queues2:
                    print("lol")
                else:
                    if file.endswith(".mp3"):
                        updateCurrentSong(file.split('.mp3')[0])
                        os.rename(file, "song"+ str(counter) +".mp3")
                        queues2.append("song"+ str(counter) +".mp3")
                        arg = "song"+ str(counter) +".mp3"
            voice.play(discord.FFmpegPCMAudio(arg), after=lambda x=None: check_queue(ctx, ctx.message.guild.id))
            await ctx.send("Playing...")
            await ctx.invoke(client.get_command('controlPanel'))
            await ctx.invoke(client.get_command('checkForLeave'))
            queues2.append(arg)
        except yt_dlp.utils.DownloadError:
            await ctx.invoke(client.get_command('error'))
    else:
        try:
            if("-play" in str(ctx.message.content)):
                arg = str(ctx.message.content).replace("-play", "")
            elif ("-p" in str(ctx.message.content)):
                arg = str(ctx.message.content).replace("-p", "")

            print(arg)


            voice = ctx.guild.voice_client
            if voice.is_playing():
                counter = len(queuesNames)
                queuesNames.append(0)
                ydl = yt_dlp.YoutubeDL(ydl_opts)
                videos = ydl.extract_info("ytsearch:"+arg, download=True)
                for file in os.listdir("./"):
                    if file in queues2:
                        print("lol")
                    else:
                        if file.endswith(".mp3"):
                            nameOfSongsInQ.append(file.split('.mp3')[0])
                            os.rename(file, "song" + str(counter) + ".mp3")
                            queues2.append("song" + str(counter) + ".mp3")
                            arg = "song" + str(counter) + ".mp3"
                source = FFmpegPCMAudio(arg)

                guild_id = ctx.message.guild.id

                if guild_id in queues:
                    queues[guild_id].append(source)
                else:
                    queues[guild_id] = [source]

                await ctx.send("Added to q")
                await ctx.invoke(client.get_command('controlPanel'))
                await ctx.invoke(client.get_command('checkForLeave'))
                return

            counter = len(queuesNames)
            queuesNames.append(0)
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            videos = ydl.extract_info("ytsearch:"+arg, download=True)
            for file in os.listdir("./"):
                if file in queues2:
                    print("lol")
                else:
                    if file.endswith(".mp3"):
                        updateCurrentSong(file.split('.mp3')[0])
                        os.rename(file, "song" + str(counter) + ".mp3")
                        queues2.append("song" + str(counter) + ".mp3")
                        arg = "song" + str(counter) + ".mp3"
            voice.play(discord.FFmpegPCMAudio(arg), after=lambda x=None: check_queue(ctx, ctx.message.guild.id))
            await ctx.send("Playing...")
            await ctx.invoke(client.get_command('controlPanel'))
            await ctx.invoke(client.get_command('checkForLeave'))
            queues2.append(arg)
        except yt_dlp.utils.DownloadError:
            await ctx.invoke(client.get_command('error'))

    #source = FFmpegPCMAudio(arg)
    #player = voice.play(source, after=lambda x=None: check_queue(ctx, ctx.message.guild.id))


@client.command(pass_context = True , name = "queue", aliases = ["q", "que"], help="please input the utube link")
async def queue(ctx):
    if len(nameOfSongsInQ) == 0:
        await ctx.send("There are no songs currently in queue to add one do -p (title or url) or -play (title or url)")
    else:
        await ctx.send("Current songs in queue are: ")
        counter = 1
        for x in nameOfSongsInQ:
            await ctx.send(str(counter) + ": " + x)
            counter = counter + 1


class Menu(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        self.ctx = 0
        self.embededM = None




    @discord.ui.button(label="▶", style=discord.ButtonStyle.green)
    async def menu1(self, button: discord.ui.Button, interaction: discord.Interaction):
        voice = discord.utils.get(client.voice_clients, guild=self.ctx.guild)
        if voice.is_paused():
            voice.resume()
        else:
            await self.ctx.send("dumbass... no audio is paused")
        await self.ctx.invoke(client.get_command('controlPanel'))

    @discord.ui.button(label="⏸", style=discord.ButtonStyle.red)
    async def menu2(self, button: discord.ui.Button, interaction: discord.Interaction):
        voice = discord.utils.get(client.voice_clients, guild=self.ctx.guild)
        if voice.is_playing():
            voice.pause()

        else:
            await self.ctx.send("dumbass... no audio is playing")
        await self.ctx.invoke(client.get_command('controlPanel'))

    @discord.ui.button(label="⏭", style=discord.ButtonStyle.blurple)
    async def menu3(self, button: discord.ui.Button, interaction: discord.Interaction):
        voice = discord.utils.get(client.voice_clients, guild=self.ctx.guild)
        voice.stop()
        await self.ctx.send("Skipped")
        songNumber = len(queuesNames2) - 1
        for file in os.listdir("./"):
            if file.endswith("song" + str(songNumber) + ".mp3"):
                os.remove(file)


    @discord.ui.button(label="Queue", style=discord.ButtonStyle.grey)
    async def menu4(self, button: discord.ui.Button, interaction: discord.Interaction):
        if len(nameOfSongsInQ) == 0:
            await self.ctx.send("There are no songs currently in queue to add one do -p (url) or -play (url)")
        else:
            value = ""
            counter = 1
            for x in nameOfSongsInQ:
                value = value + (str(counter) + ": " + x) + " \n"
                counter = counter + 1
            embed = discord.Embed(color=discord.Color.random())
            embed.set_author(name="Queue ")
            embed.add_field(name="Current songs in queue are:", value=value)
            await self.ctx.channel.send(embed=embed)

            await self.ctx.invoke(client.get_command('controlPanel'))




@client.command(pass_context = True , name = "controlPanel", aliases = ["cp", "control", "controls", "player"], help="please input the utube link")
async def controlPanel(ctx):

    if not (msg1 == []):
        await msg1[0].delete()
        msg1.pop(0)

    if not (msg2 == []):
        await msg2[0].delete()
        msg2.pop(0)

    embed = discord.Embed(color=discord.Color.random())
    embed.set_author(name = "Control Panel")
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        embed.add_field(name="Paused", value="Currently paused. Press ▶ to contine" )


    if len(currentSong) > 0:

        if nameOfSongsInQ == []:
            value = "-------------------"
        else:
            value = "next song is: " + nameOfSongsInQ[0]
        embed.add_field(name="Now Playing: " + currentSong[0], value=value)
    else:
        embed.add_field(name="End of Queue", value="There are no songs currently in queue to add one do -p (url or title) or -play (url or title)")
    m1 = await ctx.channel.send(embed=embed)
    SetMsg1(m1)
    view = Menu()
    view.ctx = ctx
    view.embededM = m1
    m2 = await ctx.channel.send(view = view)
    SetMsg2(m2)


@client.command(pass_context = True , name = "restart", help="restart")
async def restart(ctx):
    print("argv: " , sys.argv)
    print("sys executable: " ,sys.executable)
    print("restart now")
    await ctx.send("restarting the bot")
    os.execv(sys.executable, ['python'] + sys.argv)

def SetMsg1(x):
    msg1.append(x)

def SetMsg2(x):
    msg2.append(x)




client.run(TOKEN)












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