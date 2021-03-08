import os



class Util():
    @staticmethod
    def getFile(file):
        return os.path.join(os.path.dirname(__file__), file)

    @staticmethod
    def deleteFile(file):
        os.remove(Util.getFile(file))

    @staticmethod
    def fileExists(file):
        return os.path.isfile(Util.getFile(file))

    @staticmethod
    def deleteAllMP3():
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                Util.deleteFile(file)

    @staticmethod
    def renameMP3(oldName, newName):
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                if (oldName == None) and (not file in ["current.mp3", "next.mp3"]):
                    os.rename(file, newName)
                    break
                elif (oldName != None) and (file == oldName):
                    os.rename(file, newName)
                    break
