import discord
import asyncio
from datetime import datetime

import config as cfg



class Automod():
    def __init__(self):
        self.recentMessages = []

    def processMessage(self, messageObject):
        for word in cfg.WORD_BLACKLIST:
            if word.lower() in messageObject.content.lower():
                return "DELETE"
        self.recentMessages.append(messageObject)
        userCounter = {}
        for i, recentMessage in enumerate(self.recentMessages):
            if datetime.timestamp(recentMessage.created_at) + 30 < datetime.timestamp(datetime.now()):
                del self.recentMessages[i]
                continue
            if recentMessage.author.id in userCounter:
                userCounter[recentMessage.author.id] += 1
                if userCounter[recentMessage.author.id] > 10 and recentMessage.author.id == messageObject.author.id:
                    return "SPAM"
            else:
                userCounter[recentMessage.author.id] = 1
