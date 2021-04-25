# Name: Eli Estridge
# Date: 3 APR 2021
# Use: Term Loader for Validator

# Abstract: Loads the Standard & Specific Terminology files into a dictionary,
# and returns the dictionary to the validator program

# Rep invariant: terms are saved into a terminology dictionary as tuple key, value
# pairs, a copy of the dictionary is then returned

import codecs
from collections import defaultdict


# TODO: Add method to add more generic terms to .termdatabase from file


class BadFormattingError(Exception):
    def __init__(self, badLine):
        self.badLine = badLine


class TermLoader:
    def __init__(self, fileName):

        self.termDictForDatabase = defaultdict(list)
        self.termDictNoSave = defaultdict(list)

        self.specificTerms = codecs.open(
            fileName, "r", encoding="utf-8", errors="ignore"
        )

    def getTermDicts(self):
        return (
            self.termDictForDatabase.copy(),
            self.termDictNoSave.copy(),
        )  # does this actually only yield a copy?

    def closeFiles(self):
        self.specificTerms.close()

    def loadTerms(self):
        """Saves source: target key values pairs in a dictionary.
        The keys and values are respectively saved as phrase tuples."""

        doNotAddToDatabase = False  # All terms before @@@ flag are added to database

        for line in self.specificTerms.readlines():

            if self.isDatabaseFlag(line):
                doNotAddToDatabase = True

            elif self.isComment(line):
                continue

            else:
                if self.wellFormatted(line):
                    sourceTerm, targetTerm = self.cleanSplit(line)
                    if not doNotAddToDatabase:
                        self.termDictForDatabase[sourceTerm].append(targetTerm)

                    else:
                        self.termDictNoSave[sourceTerm].append(targetTerm)

                else:
                    raise BadFormattingError(line)

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
            return False
        return True

    def cleanSplit(self, line):
        """splits at delimiter and removes excess spacing"""
        src, tgt = line.rstrip().lower().split(",")
        return self.removeChineseMarkings(src), self.removeSpace(tgt)

    def removeChineseMarkings(self, termString):
        phrase = []

        for char in termString:
            if char != " " and char != "-" and char != "/":
                phrase.append(char)
        return tuple(phrase)

    def removeSpace(self, termString):
        """returns tuples for source word and target word"""
        phrase = []
        currentTerm = []
        for char in termString:
            if char == " " or char == "-" or char == "/":  # no dashes or "/" allowed
                if currentTerm:
                    phrase.append("".join(currentTerm))
                    currentTerm = []
            else:
                currentTerm.append(char)
        if currentTerm:
            phrase.append("".join(currentTerm))

        return tuple(phrase)
