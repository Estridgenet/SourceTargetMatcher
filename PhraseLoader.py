# Name: Eli Estridge
# Date: 3 APR 2021
# Use: Term Loader for Validator

# Abstract: Loads the Standard & Specific Terminology files into a dictionary,
# and returns the dictionary to the validator program

# Rep invariant: terms are saved into a terminology dictionary as tuple key, value
# pairs, a copy of the dictionary is then returned

import codecs
from collections import defaultdict


class TermLoader:
    def __init__(self, fileName):
        self.termDictForDatabase = defaultdict(list)
        self.termDictNoSave = defaultdict(list)

        """
        self.standTerms = codecs.open(
            "StandardWords.txt", "r", encoding="utf-8", errors="ignore"
        )
        """
        self.specificTerms = codecs.open(
            fileName, "r", encoding="utf-8", errors="ignore"
        )

    def getTermDicts(self):
        return self.termDictForDatabase.copy(), self.termDictNoSave.copy()

    def closeFiles(self):
        # self.standTerms.close()
        self.specificTerms.close()

    def loadTerms(self):
        """
        for line in self.standTerms.readlines():
            if self.isComment(line):
                continue
            if self.wellFormatted(line):
                sourceTerm, targetTerm = self.cleanSplit(line)
                self.termDict[sourceTerm] = targetTerm
        """
        doNotAddToDatabase = False

        for line in self.specificTerms.readlines():

            if self.isDatabaseFlag(line):
                doNotAddToDatabase = True
                continue
            if self.isComment(line):
                continue

            if self.wellFormatted(line):
                sourceTerm, targetTerm = self.cleanSplit(line)
                if not doNotAddToDatabase:
                    self.termDictForDatabase[sourceTerm].append(targetTerm)
                else:
                    print("beep", sourceTerm, targetTerm)
                    self.termDictNoSave[sourceTerm].append(targetTerm)

        self.closeFiles()

    def isDatabaseFlag(self, line):
        return (
            line.rstrip() == "@@@"
        )  # marks that the following terms should not be added to database

    def isComment(self, line):
        return line[0] == "#"

    def wellFormatted(self, line):
        """checks for correct delimiter, and prompts user if
        incorrect delimiter is used"""
        delimiter = ","
        if delimiter not in line:
            print("The following term does not have correct delimiting:", line)
            return False
        return True

    def cleanSplit(self, line):
        """splits at delimiter and removes excess spacing"""
        src, tgt = line.rstrip().lower().split(",")
        return self.removeSpace(src), self.removeSpace(tgt)

    def removeSpace(self, termString):
        """returns tuples for source word and target word"""
        phrase = []
        currentTerm = []
        for char in termString:
            if char == " ":
                if currentTerm:
                    phrase.append("".join(currentTerm))
                    currentTerm = []
            else:
                currentTerm.append(char)
        if currentTerm:
            phrase.append("".join(currentTerm))
        return tuple(phrase)
