import sys
from collections import defaultdict
import PhraseLoader

# TODO: urgent: remove own database paths


class DatabaseHelper:
    """Simple Database to store terms with relevant IPC codes.

    Terms are are stored into '.termDatabase' in a user-defined DATABASEPATH
    below. Terms are stored using comma delimiters in the following manner:
    'IPC,SOURCE,TARGET' e.g. 'G02W,官僚主义,bureaucracy'. Terms of a same
    source and/or same IPC can be saved with different targets. Generic terms
    (e.g. patent-related terminology) can be saved under 'GEN'.
    """

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

    def populateDatabase(self, linesList):
        """Creates dictionary of database entries from input list.

        Args:
            linesList (list): list of strings representing entries in database.

        Returns:
            ipcDict (dict): dictionary with IPC codes as keys and dictionary of
            source/target pairs as values.
        """

        ipcDict = defaultdict(dict)
        for line in linesList:
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
        """Get ipc-specific dictionary and generic dictionary from database."""
        return {**self.database[ipc], **self.database["GEN"]}

    def setTerms(self, termDict, ipc):
        """Add new IPC-code based entries into database.

        Args:
            termDict (dict): dictionary of source words as keys and lists of target
            words as values.
            ipc (string): IPC code to save terms under.
        """

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
        """Write database dictionary entries back to .termDatabase file."""

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


if __name__ == "__main__":
    """Basic validator-independent term-adding functionality for database.

    Args (from sys):
        argv[1]: "-add" -- flag to add entries into database
        argv[2]: "<IPCCODE> -- IPC code for which entries are added under.
                    if adding generic terms, use "GEN"
        argv[3]: filepath for term file.
    """

    if sys.argv[1] == "-add":

        # Use term loader to grab terms from file
        IPC = sys.argv[2]
        terms = PhraseLoader.TermLoader(sys.argv[3])
        terms.loadTerms()
        termsForDB, _ = terms.getTermDicts()

        # Load database and set terms
        db = DatabaseHelper()
        db.setTerms(termsForDB, IPC)
        db.updateDatabase()

    else:
        print("Unsupported argument.  Try '-add <IPCCODE>' to add terms")
