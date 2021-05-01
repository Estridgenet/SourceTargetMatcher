# Name: Eli Estridge
# Date: 3 APR 2021
# Use: Term Loader for Validator

# Abstract: Loads the Standard & Specific Terminology files into a dictionary,
# and returns the dictionary to the validator program

# Rep invariant: terms are saved into a terminology dictionary as tuple key, value
# pairs, a copy of the dictionary is then returned

import codecs
from collections import defaultdict


class BadFormattingError(Exception):
    """Exception for lines not formatted in accordance with the preset format.

    Args:
        badLine (string), line formatted incorrectly.
    """

    def __init__(self, badLine):
        self.badLine = badLine


class TermLoader:
    """Retrieve source/target pairs from source file using preset format

    Args:
        fileName (string): string-based file path for UTF-8 document.
    """

    def __init__(self, fileName):

        self.termDictForDatabase = defaultdict(list)
        self.termDictNoSave = defaultdict(list)

        self.specificTerms = codecs.open(
            fileName, "r", encoding="utf-8", errors="ignore"
        )

    def getTermDicts(self):
        """Retrieve terms read in from file.

        Returns:
            Tuple of 1. terms to be saved into database, and
                    2. terms not being saved.
        """
        return (
            self.termDictForDatabase.copy(),
            self.termDictNoSave.copy(),
        )  # does this actually only yield a copy?

    def closeFiles(self):
        """Close read in file."""
        self.specificTerms.close()

    def loadTerms(self):
        """Saves source: target key values pairs in a dictionary.
        The keys and values are respectively saved as phrase tuples."""

        doNotAddToDatabase = False  # All terms before @@@ flag are added to database

        for line in self.specificTerms.readlines():

            if self.isDatabaseFlag(line):  # check for @@@ flag
                doNotAddToDatabase = True

            elif self.isComment(line) or self.isEmptyLine(
                line
            ):  # check for '#' comment flag or no content
                continue

            else:
                if self.wellFormatted(line):  # check for correct delimiter, ','
                    sourceTerm, targetTerm = self.cleanSplit(line)
                    if not doNotAddToDatabase:
                        self.termDictForDatabase[sourceTerm].append(targetTerm)

                    else:
                        self.termDictNoSave[sourceTerm].append(targetTerm)

                else:
                    raise BadFormattingError(line)

        self.closeFiles()

    def isDatabaseFlag(self, line):
        """Check to see if following terms should not be added to database."""
        return line.rstrip() == "@@@"

    def isComment(self, line):
        """Check to see if comment flag is present."""
        return line[0] == "#"

    def wellFormatted(self, line):
        """checks for correct (EN or ZH) delimiter.

        Args:
            line (string) line from read in file."""

        delimiter = (",", "，")
        if delimiter[0] not in line and delimiter[1] not in line:
            return False
        return True

    def cleanSplit(self, line):
        """Split at delimiter and remove excess spacing."""

        line = line.replace("，", ",")  # replace chinese delimiter if necessary
        src, tgt = line.rstrip().lower().split(",")
        return self.removeChineseMarkings(src), self.removeSpace(tgt)

    def removeChineseMarkings(self, termString):
        phrase = []

        for char in termString:
            if char != " " and char != "-" and char != "/":
                phrase.append(char)
        return tuple(phrase)

    def removeSpace(self, termString):
        """Return tuples for target word."""
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

    def isEmptyLine(self, line):
        """Check for contentless or space-only string."""
        return line.rstrip(" \n\t\r") == ""
