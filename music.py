import discord
import asyncio
import youtube_dl
import requests
import time

from util import Util



class Music():
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',}]}
        self.voiceClient = None
        self.queue = []
        Util.deleteAllMP3()

    async def connect(self, voiceChannel):
        self.voiceClient = await voiceChannel.connect()

    def addToQueue(self, url):
        try:
            with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                dictMeta = ydl.extract_info(url, download=False)
        except youtube_dl.utils.DownloadError:
            return False
        else:
            self.queue.append(Song(url, dictMeta["title"]))
            return True

    def downloadSong(self, song):
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([song.url])

    def playNext(self):
        if len(self.queue) == 0:
            return
        if not Util.fileExists("current.mp3"):
            self.downloadSong(self.queue[0])
            Util.renameMP3(None, "current.mp3")
        self.voiceClient.play(discord.FFmpegPCMAudio(Util.getFile("current.mp3")), after=self.songEnded)
        if len(self.queue) >= 2:
            self.downloadSong(self.queue[1])
            Util.renameMP3(None, "next.mp3")

    def songEnded(self, error):
        del self.queue[0]
        Util.deleteFile("current.mp3")
        if Util.fileExists("next.mp3"):
            Util.renameMP3("next.mp3", "current.mp3")
            time.sleep(2)
            self.playNext()



class Song():
    def __init__(self, url, title):
        self.url = url
        self.title = title
