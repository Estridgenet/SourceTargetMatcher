# Name: Eli Estridge
# Date: 3 APR 2021
# Use: Term Loader for Validator

# Abstract: Loads the Standard & Specific Terminology files into a dictionary,
# and returns the dictionary to the validator program

# Rep invariant: terms are saved into a terminology dictionary as tuple key, value
# pairs, a copy of the dictionary is then returned


class TermLoader:
    def __init__(self, fileName):
        self.termDict = dict()
        self.standTerms = open("StandardWords.txt", "r")
        self.specificTerms = open(fileName, "r")

    def getTermDict(self):
        return self.termDict.copy()  # is this a real copy?

    def closeFiles(self):
        self.standTerms.close()
        self.specificTerms.close()

    def loadTerms(self):
        for line in self.standTerms.readlines():
            if self.isComment(line):
                continue
            if self.wellFormatted(line):
                sourceTerm, targetTerm = self.cleanSplit(line)
                self.termDict[sourceTerm] = targetTerm

        for line in self.specificTerms.readlines():
            if self.isComment(line):
                continue
            if self.wellFormatted(line):
                sourceTerm, targetTerm = self.cleanSplit(line)
                self.termDict[sourceTerm] = targetTerm

        self.closeFiles()

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
