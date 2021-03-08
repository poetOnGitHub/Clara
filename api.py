import discord
import asyncio
import requests
import json

import config as cfg



class API():
    def __init__(self):
        self.fivemChannel = None
        self.statsMessage = None

    def getStatsEmbed(self):
        embed = discord.Embed(title="FIVEM SERVER STATS", description="FiveM Server", color=0x0000FF)
        try:
            serverInfo = requests.get(f"http://{cfg.FIVEM_SERVER_IP}/info.json").json()
            serverPlayers = requests.get(f"http://{cfg.FIVEM_SERVER_IP}/players.json").json()
        except Exception:
            embed.add_field(name="Server Status", value="`OFFLINE`", inline=True)
        else:
            embed.add_field(name="Server Status", value="`ONLINE`", inline=True)
            embed.add_field(name="Player Count", value=f"`{len(serverPlayers)}`", inline=True)
            embed.add_field(name="Available Slots", value=f"`{int(serverInfo['vars']['sv_maxClients']) - len(serverPlayers)}`", inline=True)
            players = ""
            for player in serverPlayers:
                players += f"`{player}`, "
            players = players[:-2]
            if players == "":
                players = "`N/A`"
            embed.add_field(name="Current Players", value=players, inline=True)
        return embed

    async def updateStats(self, messageID=None):
        statsEmbed = self.getStatsEmbed()
        if self.statsMessage != None:
            await self.statsMessage.edit(embed=statsEmbed)
            return self.statsMessage
        elif messageID != None:
            async for oldMessage in self.fivemChannel.history():
                if oldMessage.id == messageID:
                    self.statsMessage = oldMessage
                    await self.statsMessage.edit(embed=statsEmbed)
                    return self.statsMessage
                    break
            else:
                return await self.fivemChannel.send(embed=statsEmbed)
        else:
            return await self.fivemChannel.send(embed=statsEmbed)
