from collections import defaultdict
import re

# Basic (1) (2) (3), (S1), (S2)
# Hard (S1, S2)
# must avoid (my name is .....)
# Perhaps we should include unparenthesized strings such as
# CAR SEG M51, in this case we might just look for all caps or
# caps +
# should skip drawings and title
# can also compare numbers since they should all be the same...


class CompareReferenceElements:
    """Compare special markers shared by the source and target texts.

    Args:
        matches (list of lists): matched source/target strings (see ExtractContent).
        output (file): output file to write to.
    """

    def __init__(self, matches, output):
        self.matches = matches
        self.outputfile = output
        self.curState = None

        self.punctuationSet = set(
            [
                ",",
                ".",
                "?",
                ";",
                "。",
                "'",
                '"',
                "”",
                "“",
                "，",
                "、",
                "\n",
                "",
                ":",
                "：",
                "/",
                "?",
                "!",
                "\t",
                "(",
                ")",
                "-",
            ]
        )
        self.replaceDict = {
            "（": "(",
            "）": ")",
            "，": ",",
            "“": '"',
            "”": '"',
            "‘": "'",
            "’": "'",
            "。": ".",
            "！": "!",
            "《": "<",
            "》": ">",
        }

    def CompareTexts(self):
        for matchList in self.matches:
            sourceCount = defaultdict(int)
            targetCount = defaultdict(int)

            idnum, source, target = matchList
            source = self.replaceChinesePunctuation(source)
            pass

    def removePunctuation(self, word):
        return "".join([char for char in word if char not in self.punctuationSet])

    def replaceChinesePunctuation(self, string):
        return "".join(
            [i if i not in self.replaceDict else self.replaceDict[i] for i in string]
        )

    def loadString(self, string):
        """Save string as current state and set position to zero."""
        self.curState = [string, 0]

    def getNextChar(self):
        """Return next char from string."""
        if self.curState[1] < len(self.curState[0]):
            nextChar = self.curState[0][self.curState[1]]
            self.curState[1] += 1
        else:
            nextChar = ""  # End of String
        return nextChar

    def getReferenceNumbers(self, string, countDict):
        # reference number format: (content)
        # content: element[, element]
        # element: chars&numbers
        # we can recursively go through document and look for matches
        # but we need to have something that yields chars for us
        pass

    def getContent(self):
        """Obtains content from inside ()"""
        elements = []

        while True:
            element, shouldContinue = self.getElement()
            if element == "": # invalid element
                return []

            elements.append(element)
            if shouldContinue is False:
                break

        return elements

    def getElement(self):
        element = []

        while True:
            nextChar = self.getNextChar()
            if nextChar == "":
                return "", False
            elif nextChar == " ":
                return "", False
            elif nextChar == ")":
                return "".join(element), False
            elif nextChar == ",":
                return "".join(element), True
            elif self.isChineseChar(nextChar):
                return "", False
            else:
                element.append(nextChar)

        return "", False  # shouldn't get here

    def isChineseChar(self, char):
        # Trick by Ceshine Lee
        return True if (re.search("[\u4e00-\u9FFF]", char)) else False

    def getNumbers(self):
        # TODO: number functionality
        pass
