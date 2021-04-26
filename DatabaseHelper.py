### Simple database for dict terms
import sys
from collections import defaultdict

#TODO: Set a location for database files on windows and linux
#TODO: read general terms from a txt file and add them to the dictionary

class DatabaseHelper:
    def __init__(self):

        if sys.platform.startswith("win"):
            self.DATABASEPATH = r"C:/Users/Eli/Desktop/PatentValidator/SourceTargetMatcher/.termDatabase"
        else:
            self.DATABASEPATH = r"/home/estridgenet/Dropbox/Programming/Python/PatentValidate/PatentValidator/.termDatabase"

        database = open(
            self.DATABASEPATH,
            "r",
        )
        self.database = self.populateDatabase(database.readlines())
        database.close()

    def populateDatabase(self, dataList):
        """simple IPC, SOURCE, TARGET"""
        ipcDict = defaultdict(dict)
        for line in dataList:
            ipc, source, target = line.strip(" \n").split(",")
            if source in ipcDict[ipc]:
                ipcDict[ipc][tuple([char for char in source])].append(
                    tuple(target.split(" "))
                )

            else:
                ipcDict[ipc][tuple([char for char in source])] = [
                    tuple(target.split(" "))
                ]

        return ipcDict

    def getTerms(self, ipc):
        return {**self.database[ipc], **self.database["GEN"]}

    def setTerms(self, termDict, ipc):
        for key, valueList in termDict.items():
            if key in self.database[ipc]:
                self.database[ipc][key] += valueList
            else:
                self.database[ipc][key] = valueList

    def makeString(self, lang, tup):
        if lang == "ZH":
            return "".join([i for i in tup if i not in ("", " ")])

        return " ".join([i for i in tup if i not in ("", " ")])

    def updateDatabase(self):
        dataBaseEntries = set()
        newDatabase = open(self.DATABASEPATH, "w")
        for ipcCode in self.database.keys():
            for source, targetList in self.database[ipcCode].items():
                for entry in targetList:
                    dataBaseEntries.add(
                        "%s,%s,%s\n"
                        % (
                            ipcCode,
                            self.makeString("ZH", source),
                            self.makeString("EN", entry),
                        )
                    )
        for e in sorted(dataBaseEntries):
            newDatabase.write(e)
        newDatabase.close()
