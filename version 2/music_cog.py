from ast import alias
import discord
import asyncio
import sys
import os
from discord.ext import commands
from yt_dlp import YoutubeDL


msg1 = []
msg2 = []


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.ctx = None
        self.bot = bot
        self.cSong = None
        # all the music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}

        self.vc = None
        self.currentSong = None

        self.doOnce = False

    # searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:
                return False

        return {'source': info['url'], 'title': info['title']}

    def play_next(self):
        print("NEXT")
        if len(self.music_queue) > 0:
            self.is_playing = True

            # get the first url
            m_url = self.music_queue[0][0]['source']

            # remove the first element as you are currently playing it
            self.currentSong = self.music_queue[0]
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            if not self.vc.is_playing():
                self.currentSong = None
            self.is_playing = False

    # infinite loop checking
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            # try to connect to voice channel if you are not already connected
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                # in case we fail to connect
                if self.vc == None:
                    await ctx.send("Could not connect to the voice channel")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            # remove the first element as you are currently playing it
            self.currentSong = self.music_queue[0]
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @commands.command(name="play", aliases=["p", "playing"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):

        self.ctx = ctx
        query = " ".join(args)



        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            # you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        elif self.is_paused:
            self.vc.resume()
        else:
            await ctx.send("adding song...")
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send(
                    "Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.")
            else:
                await ctx.send("Song added to the queue")
                self.music_queue.append([song, voice_channel])


                if self.is_playing == False:
                    await self.play_music(ctx)
                await ctx.invoke(self.bot.get_command('controlPanel'))
                await ctx.invoke(self.bot.get_command('checkForLeave'))
                    # await self.checkForNextSong(ctx= ctx)
                    # await self.checkForLeave(ctx= ctx)



    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()
        await ctx.invoke(self.bot.get_command('controlPanel'))


    @commands.command(name="resume", aliases=["r"], help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
        self.vc.resume()
        await ctx.invoke(self.bot.get_command('controlPanel'))

    @commands.command(pass_context=True, name="checkForLeave", help="checkForLeave")
    async def checkForLeave(self, ctx):
        voice = ctx.channel.guild.voice_client
        time = 0
        while True:
            if not (self.currentSong == self.cSong):
                print("diff song")
                self.cSong = self.currentSong
                await ctx.invoke(self.bot.get_command('checkForLeave'))
                await ctx.invoke(self.bot.get_command('controlPanel'))
            print(time)
            await asyncio.sleep(5)
            time = time + 5
            if voice.is_playing() and not voice.is_paused():
                time = 0
            if time == 300:
                await voice.disconnect()
                await ctx.send(
                    "Left due to inactivity restarting bot to ensure everything keeps working as intended. Give him a second :)")
                await ctx.invoke(self.bot.get_command('restart'))
            if not voice.is_connected():
                break
        self.doOnce = False

    @commands.command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx):
        temp = None
        if len(self.music_queue) == 1:
            temp = self.music_queue[0][0]['title']
        if self.vc != None and self.vc:
            self.vc.stop()
            # try to play next in the queue if it exists
            #if self.vc.is_playing():
             #   self.is_paused = False
              #  self.is_playing = True
               # self.currentSong = temp

            await ctx.invoke(self.bot.get_command('controlPanel'))


    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        counter = 1
        for i in range(0, len(self.music_queue)):
            counter += counter + 1
            # display a max of 5 songs in the current queue
            if (i > 4): break
            retval += str(i + 1) + ": " + self.music_queue[i][0]['title'] + "\n"


        if retval != "":
            embed = discord.Embed(color=discord.Color.random())
            embed.set_author(name="Queue ")
            embed.add_field(name="Current songs in queue are:", value=retval)
            await ctx.channel.send(embed=embed)
        else:
            await ctx.send("No music in queue")
        await ctx.invoke(self.bot.get_command('controlPanel'))


    @commands.command(name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        await ctx.invoke(self.bot.get_command('controlPanel'))
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Music queue cleared")


    @commands.command(name="leave", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()

    @commands.command(pass_context=True, name="controlPanel", aliases=["cp", "control", "controls", "player"],
                      help="please input the utube link")
    async def controlPanel(self, ctx):
        print(self.currentSong)
        if not (msg1 == []):
            await msg1[0].delete()
            msg1.pop(0)

        if not (msg2 == []):
            await msg2[0].delete()
            msg2.pop(0)

        embed = discord.Embed(color=discord.Color.random())
        embed.set_author(name="Control Panel")
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_paused():
            embed.add_field(name="Paused", value="Currently paused. Press ▶ to contine")

        if not (self.currentSong == None):

            if len(self.music_queue) == 0:
                value = "-------------------"
            else:
                value = "next song is: " + str(self.music_queue[0][0]['title'])
            embed.add_field(name="Now Playing: " + str(self.currentSong[0]['title']), value=value)
        else:
            embed.add_field(name="End of Queue",
                            value="There are no songs currently in queue to add one do -p (url or title) or -play (url or title)")
        m1 = await ctx.channel.send(embed=embed)
        SetMsg1(m1)
        view = Menu(self.bot, self)
        view.ctx = ctx
        view.embededM = m1
        m2 = await ctx.channel.send(view=view)
        SetMsg2(m2)

    @commands.command(pass_context=True, name="restart", help="restart")
    async def restart(self, ctx):
        print("argv: ", sys.argv)
        print("sys executable: ", sys.executable)
        print("restart now")
        await ctx.send("restarting the bot")
        os.execv(sys.executable, ['python'] + sys.argv)






class Menu(discord.ui.View):
    def __init__(self, bot, secondSelf):
        super().__init__()
        self.value = None
        self.ctx = 0
        self.embededM = None
        self.bot = bot
        self.secondSelf = secondSelf




    @discord.ui.button(label="▶", style=discord.ButtonStyle.green)
    async def menu1(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.ctx.invoke(self.bot.get_command('resume'))


    @discord.ui.button(label="⏸", style=discord.ButtonStyle.red)
    async def menu2(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.ctx.invoke(self.bot.get_command('pause'))


    @discord.ui.button(label="⏭", style=discord.ButtonStyle.blurple)
    async def menu3(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.ctx.invoke(self.bot.get_command('skip'))



    @discord.ui.button(label="Queue", style=discord.ButtonStyle.grey)
    async def menu4(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.ctx.invoke(self.bot.get_command('queue'))









def SetMsg1(x):
    if len(msg1) > 1:
        msg1.clear()
        msg1.append(x)
        return
    if len(msg1) == 1:
        msg1[0] = x
        return
    msg1.append(x)

def SetMsg2(x):
    if len(msg2) > 1:
        msg2.clear()
        msg2.append(x)
        return
    if len(msg2) == 1:
        msg2[0] = x
        return
    msg2.append(x)



