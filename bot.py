import discord
import asyncio

import config as cfg
from music import Music
from responses import Responses, QuestionHandler
from automod import Automod
from database import Database
from util import Util
from api import API



music = Music()
questionHandler = QuestionHandler()
automod = Automod()
database = Database()
api = API()



class Bot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_task = self.loop.create_task(self.backgroundLoop())

    def isAdmin(self, memberObject):
        for roleObject in memberObject.roles:
            if roleObject.id in cfg.ADMIN_ROLE_IDS:
                return True
        return False

    def hasRole(self, memberObject, roleToCheck):
        for roleObject in memberObject.roles:
            if roleObject.id == roleToCheck.id:
                return True
        return False

    async def on_ready(self):
        await bot.wait_until_ready()
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="NADOJ | !help"))
        print (bot.user.name + " is ready")
        print ("ID: " + str(bot.user.id))
        guild = bot.get_guild(cfg.SERVER_ID)
        self.mutedRole = guild.get_role(cfg.MUTED_ROLE_ID)
        self.ticketsChannel = guild.get_channel(cfg.TICKETS_CHANNEL_ID)
        self.announcementsChannel = guild.get_channel(cfg.ANNOUNCEMENTS_CHANNEL_ID)

    async def on_message(self, messageObject):
        if messageObject.author.bot or messageObject.guild == None: return
        parameters = messageObject.content.lower().split()

        automodStatus = automod.processMessage(messageObject)
        if automodStatus == "DELETE":
            await messageObject.delete()
        elif automodStatus == "SPAM":
            if not self.hasRole(messageObject.author, self.mutedRole):
                await messageObject.author.add_roles(*[self.mutedRole])
                await Responses.sendInfo(messageObject.channel, "Automod", f"{messageObject.author} has been muted for spamming.", 0xFF0000)

        existingTicket = questionHandler.getQuestion("ticket", messageObject.author.id, messageObject.channel.id)
        if existingTicket != None:
            await Responses.sendInfo(self.ticketsChannel, "Ticket", messageObject.content, 0x0000FF, messageObject.author)
            await Responses.sendSuccess(messageObject.channel, "Your ticket has been submitted.")
            questionHandler.deleteQuestion("ticket", messageObject.author.id)
        existingAnnouncement = questionHandler.getQuestion("announcement", messageObject.author.id, messageObject.channel.id)
        if existingAnnouncement != None:
            await Responses.sendInfo(self.announcementsChannel, "Announcement", messageObject.content, 0x0000FF)
            await Responses.sendSuccess(messageObject.channel, "Announcement sent.")
            questionHandler.deleteQuestion("announcement", messageObject.author.id)

        if parameters[0] == f"{cfg.COMMAND_PREFIX}help":
            await Responses.sendHelp(messageObject.channel)

        elif parameters[0] == f"{cfg.COMMAND_PREFIX}warn":
            if not self.isAdmin(messageObject.author): return
            if len(parameters) < 3 or messageObject.mentions == []: return
            targetMember, warning = messageObject.mentions[0], " ".join(messageObject.content.split()[2:])
            database.addWarning(targetMember.id, warning)
            await Responses.sendInfo(messageObject.channel, "Warning", f"{targetMember.mention} {warning}", 0xFF0000)

        elif parameters[0] == f"{cfg.COMMAND_PREFIX}warnings":
            if not self.isAdmin(messageObject.author): return
            if len(parameters) < 2 or messageObject.mentions == []: return
            targetMember = messageObject.mentions[0]
            listText = ""
            for i, warningData in enumerate(database.getWarnings(targetMember.id)):
                listText += f"**{i + 1})** {warningData['warning']}\n\n"
            await Responses.sendInfo(messageObject.channel, f"Warnings For {targetMember}", listText, 0x0000FF)

        elif parameters[0] == f"{cfg.COMMAND_PREFIX}mute":
            if not self.isAdmin(messageObject.author): return
            if len(parameters) < 2 or messageObject.mentions == []: return
            targetMember = messageObject.mentions[0]
            await targetMember.add_roles(*[self.mutedRole])
            await Responses.sendSuccess(messageObject.channel, f"{targetMember} has been muted.")

        elif parameters[0] == f"{cfg.COMMAND_PREFIX}unmute":
            if not self.isAdmin(messageObject.author): return
            if len(parameters) < 2 or messageObject.mentions == []: return
            targetMember = messageObject.mentions[0]
            await targetMember.remove_roles(*[self.mutedRole])
            await Responses.sendSuccess(messageObject.channel, f"{targetMember} has been unmuted.")

        elif parameters[0] == f"{cfg.COMMAND_PREFIX}kick":
            if not self.isAdmin(messageObject.author): return
            if len(parameters) < 2 or messageObject.mentions == []: return
            targetMember = messageObject.mentions[0]
            await messageObject.guild.kick(targetMember)
            await Responses.sendSuccess(messageObject.channel, f"{targetMember} has been kicked.")

        elif parameters[0] == f"{cfg.COMMAND_PREFIX}ban":
            if not self.isAdmin(messageObject.author): return
            if len(parameters) < 2 or messageObject.mentions == []: return
            targetMember = messageObject.mentions[0]
            await messageObject.guild.ban(targetMember)
            await Responses.sendSuccess(messageObject.channel, f"{targetMember} has been banned.")


        elif parameters[0] == f"{cfg.COMMAND_PREFIX}ticket":
            existingTicket = questionHandler.getQuestion("ticket", messageObject.author.id)
            if existingTicket != None:
                questionHandler.deleteQuestion("ticket", messageObject.author.id)
            questionHandler.addQuestion("ticket", messageObject.author.id, messageObject.channel.id)
            await Responses.sendInfo(messageObject.channel, "New Ticket", "Send your ticket in this channel. The next message you send will be used as your ticket.", 0x0000FF)

        elif parameters[0] == f"{cfg.COMMAND_PREFIX}announce":
            if not self.isAdmin(messageObject.author): return
            existingAnnouncement = questionHandler.getQuestion("announcement", messageObject.author.id)
            if existingAnnouncement != None:
                questionHandler.deleteQuestion("announcement", messageObject.author.id)
            questionHandler.addQuestion("announcement", messageObject.author.id, messageObject.channel.id)
            await Responses.sendInfo(messageObject.channel, "New Announcement", "Send your announcement in this channel. The next message you send will be used as your announcement.", 0x0000FF)

        elif parameters[0] == f"{cfg.COMMAND_PREFIX}play":
            if messageObject.author.voice == None:
                await Responses.sendError(messageObject.channel, "You must be in a voice channel to use this command!")
                return
            if len(parameters) >= 2:
                await Responses.sendInfo(messageObject.channel, "Music", f"Downloading...", 0xFF0000)
                if not music.addToQueue(messageObject.content.split()[1]):
                    await Responses.sendError(messageObject.channel, "Invalid youtube url or an error occurred!")
                    return
                if len(music.queue) == 2:
                    music.downloadSong(music.queue[1])
                    Util.renameMP3(None, "next.mp3")
                await Responses.sendInfo(messageObject.channel, "Music", f"Added to song queue: `{music.queue[-1].title}`", 0xFF0000)
            elif len(music.queue) == 0:
                await Responses.sendError(messageObject.channel, "There are no songs currently in the queue!")
                return
            if music.voiceClient == None:
                await music.connect(messageObject.author.voice.channel)
            if not music.voiceClient.is_playing():
                music.playNext()
                await Responses.sendInfo(messageObject.channel, "Music", f"Now playing `{music.queue[0].title}`", 0xFF0000)

        elif parameters[0] == f"{cfg.COMMAND_PREFIX}stop":
            if messageObject.author.voice == None:
                await Responses.sendError(messageObject.channel, "You must be in a voice channel to use this command!")
                return
            if not music.voiceClient.is_playing(): return
            await music.voiceClient.disconnect()
            await Responses.sendInfo(messageObject.channel, "Music", f"Music stopped", 0xFF0000)

        elif parameters[0] == f"{cfg.COMMAND_PREFIX}skip":
            if messageObject.author.voice == None:
                await Responses.sendError(messageObject.channel, "You must be in a voice channel to use this command!")
                return
            if not music.voiceClient.is_playing(): return
            if len(music.queue) < 2:
                await Responses.sendError(messageObject.channel, "There are no more songs in the queue!")
                return
            music.voiceClient.stop()
            await Responses.sendInfo(messageObject.channel, "Music", f"Skipping to next song...", 0xFF0000)
            currentChannel = music.voiceClient.channel
            await music.voiceClient.disconnect()
            await music.connect(currentChannel)

        elif parameters[0] == f"{cfg.COMMAND_PREFIX}pause":
            if messageObject.author.voice == None:
                await Responses.sendError(messageObject.channel, "You must be in a voice channel to use this command!")
                return
            if not music.voiceClient.is_playing(): return
            if music.voiceClient.is_paused(): return
            music.voiceClient.pause()
            await Responses.sendInfo(messageObject.channel, "Music", f"Music has been paused", 0xFF0000)

        elif parameters[0] == f"{cfg.COMMAND_PREFIX}unpause":
            if messageObject.author.voice == None:
                await Responses.sendError(messageObject.channel, "You must be in a voice channel to use this command!")
                return
            if not music.voiceClient.is_paused(): return
            music.voiceClient.resume()
            await Responses.sendInfo(messageObject.channel, "Music", f"Music has been resumed", 0xFF0000)

        elif parameters[0] in [f"{cfg.COMMAND_PREFIX}q", f"{cfg.COMMAND_PREFIX}queue"]:
            if messageObject.author.voice == None:
                await Responses.sendError(messageObject.channel, "You must be in a voice channel to use this command!")
                return
            if music.queue == []:
                listText = "No songs in the queue"
            else:
                listText = ""
            for i, song in enumerate(music.queue):
                listText += f"**{i + 1})** `{song.title}`\n"
            await Responses.sendInfo(messageObject.channel, "Music Queue", listText, 0xFF0000)



    async def backgroundLoop(self):
        await self.wait_until_ready()
        api.fivemChannel = bot.get_guild(cfg.SERVER_ID).get_channel(cfg.FIVEM_CHANNEL_ID)
        if api.fivemChannel == None:
            print("FiveM Stats Channel not found!")
            return
        fivemMessageID = database.getFivemMessageID()
        while not self.is_closed():
            try:
                fivemMessage = await api.updateStats(messageID=fivemMessageID)
                fivemMessageID = fivemMessage.id
                database.saveFivemMessageID(fivemMessageID)
            except Exception as e:
                print(f"Background loop error! - {e}")
            await asyncio.sleep(60)



bot = Bot()
bot.run(cfg.BOT_TOKEN)
