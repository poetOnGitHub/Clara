import discord
import asyncio

import config as cfg



class Responses():
    @staticmethod
    async def sendEmbed(channelObject, embed):
        try:
            return await channelObject.send(embed=embed)
        except Exception as e:
            print(e)

    @staticmethod
    async def sendInfo(channelObject, title, message, color, author=None):
        embed = discord.Embed(title=title, description=message, color=color)
        if author != None:
            embed.set_author(name=author, icon_url=author.avatar_url)
        await Responses.sendEmbed(channelObject, embed)

    @staticmethod
    async def sendSuccess(channelObject, message):
        await Responses.sendInfo(channelObject, "Success", message, 0x00FF00)

    @staticmethod
    async def sendError(channelObject, message):
        await Responses.sendInfo(channelObject, "Error", message, 0xFF0000)

    @staticmethod
    async def sendHelp(channelObject):
        helpMsg = """
        **MODERATION (Admin Only)**
        `warn @member <message>`, `warnings @member`, `mute @member`,
        `unmute @member`, `kick @member`, `ban @member`, `announce`

        **MUSIC**
        `play <url>`, `stop`, `skip`, `pause`, `unpause`,
        `queue/q`

        **MISC**
        `ticket`, `help`
        """
        await Responses.sendInfo(channelObject, "Commands", helpMsg, 0x0000FF)



class QuestionHandler():
    def __init__(self):
        self.qlist = []

    def addQuestion(self, type, userID, channelID):
        if len(self.qlist) >= 10:
            del self.qlist[0]
        self.qlist.append(Question(type, userID, channelID))

    def getQuestion(self, type, userID, channelID=None):
        for question in self.qlist:
            if question.type == type and question.userID == userID and (channelID == None or question.channelID == channelID):
                return question

    def deleteQuestion(self, type, userID):
        for i, question in enumerate(self.qlist):
            if question.type == type and question.userID == userID:
                del self.qlist[i]



class Question():
    def __init__(self, type, userID, channelID):
        self.type = type
        self.userID = userID
        self.channelID = channelID
