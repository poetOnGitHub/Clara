import sqlite3
import time

import config as cfg
from util import Util



class Database():
    def __init__(self):
        self.db = sqlite3.connect(Util.getFile("database.db"))
        self.db.row_factory = sqlite3.Row
        self.cursor = self.db.cursor()

        self.db.execute("""CREATE TABLE IF NOT EXISTS warnings (
            id          INTEGER NOT NULL,
            user_id     INTEGER NOT NULL,
            warning     TEXT    NOT NULL,
            PRIMARY KEY (id AUTOINCREMENT));""")

        self.db.execute("""CREATE TABLE IF NOT EXISTS fivem_message (
            message_id  INTEGER NOT NULL,
            PRIMARY KEY (message_id));""")


    def fetch(self, query, args=[]):
        return self.cursor.execute(query, args).fetchall()

    def execute(self, query, args=[]):
        self.cursor.execute(query, args)
        self.db.commit()

    def addWarning(self, userID, warning):
        self.execute("INSERT INTO warnings (user_id, warning) VALUES (?, ?)", [userID, warning])

    def getWarnings(self, userID):
        return self.fetch("SELECT * FROM warnings WHERE user_id=?", [userID])

    def saveFivemMessageID(self, messageID):
        self.execute("DELETE FROM fivem_message", [])
        self.execute("INSERT INTO fivem_message VALUES (?)", [messageID])

    def getFivemMessageID(self):
        messageID = self.fetch("SELECT * FROM fivem_message", [])
        if messageID != []: return messageID[0]["message_id"]
        else: return None
