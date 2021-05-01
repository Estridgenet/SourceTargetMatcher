from collections import defaultdict
import re

# TODO: unparenthesized strings? Don't think this is possible.
# TODO: skip drawings and title
# TODO: prettier strings, figure out a way to handle numbers inside parens

class CompareReferenceElements:
    """Compare reference number markers shared by the source and target texts.

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

    def closeOutputFile(self):
        ### FOR TESTING PURPOSES ONLY###
        self.outputfile.close()

    def compareTexts(self):
        """fig num frequencies in source and target content.

        Returns:
            list of non-uniform comparison results with id number.
            Formatting is (IDNUM, REFNUM, SOURCECOUNT, TARGETCOUNT).
        """

        for matchList in self.matches:

            idnum, source, target = matchList

            source = self.replaceChinesePunctuation(source)
            sourceCount = self.getSourceFigNumbers(source)
            targetCount = self.getTargetParensContent(target)

            self.outputfile.write(idnum + "\n")
            self.compareResults(sourceCount, targetCount)

            sourceCount, targetCount = self.getNumbers(source, target)

            self.compareResults(sourceCount, targetCount)

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

    def getSourceFigNumbers(self, source):
        """Retrieve valid content from inside ().

        Args:
            source (string): Source (ZH) text with punctuation replaced.

        Returns:
            Dictionary having reference numbers as key and frequency as value.
        """
        countDict = defaultdict(int)
        self.loadString(source)

        char = self.getNextChar()
        while char != "":  # EOF
            if char == "(":
                elementList = (
                    self.getSourceElements()
                )  # grab fig nums from within parens
                for e in elementList:  # add fig nums to dict
                    countDict[e] += 1
            char = self.getNextChar()

        return countDict

    def getTargetParensContent(self, target):
        """Retrieve fig number-like content from parentheses to match against
        source Fig numbers
        Args:
            target (string): Target (EN) text.

        Returns:
            dictionary having content fragments as keys and frequencies as values.
        """

        countDict = defaultdict(int)
        self.loadString(target)

        char = self.getNextChar()
        while char != "":  # EOF
            if char == "(":
                elementList = (
                    self.getTargetElements()
                )  # grab fig nums from within parens
                for e in elementList:  # add fig nums to dict
                    countDict[e] += 1
            char = self.getNextChar()

        return countDict

    #    def getContent(self):
    #        """Obtains content from inside ()"""
    #        elements = []
    #
    #        while True:
    #            element, shouldContinue = self.getElement()
    #            if element == "": # invalid element
    #                return []
    #
    #            elements.append(element)
    #            if shouldContinue is False:
    #                break
    #
    #        return elements

    def getSourceElements(self):
        """Check for valid fig num chars and retrieve valid fig nums from string.

        Returns:
            list: list of strings which are the valid fig nums. will repeat based on
            frequency.
        """
        elements = []
        element = []
        while True:
            nextChar = self.getNextChar()
            if nextChar == "":  # EOF
                return []
            elif nextChar == " ":  # space between fig nums
                if element != []:
                    elements.append("".join(element))
                    element = []
                continue
            elif nextChar == ")":  # end of fig num
                if element != []:
                    elements.append("".join(element))
                    element = []
                return elements
            elif nextChar == ",":  # delimiter between fig nums
                if element != []:
                    elements.append("".join(element))
                    element = []
                continue
            elif self.isChineseChar(nextChar):  # not a fig num
                return []
            else:  # valid ref number char
                element.append(nextChar)

        return []  # shouldn't get here

    def getTargetElements(self):
        """Grabs all fig-number like items from within parentheses.

        Returns:
            list: list of strings representing elements in parens. will repeat based on
            frequency.
        """
        elements = []
        element = []
        while True:
            nextChar = self.getNextChar()
            if nextChar == "":  # EOF
                return elements
            elif nextChar == " ":  # space between elements
                if element != []:
                    elements.append("".join(element))
                    element = []
                continue
            elif nextChar == ")":  # end of fig num
                if element != []:
                    elements.append("".join(element))
                return elements
            elif nextChar == ",":  # delimiter between fig nums
                if element != []:
                    elements.append("".join(element))
                    element = []
                continue
            else:  # valid char
                element.append(nextChar)

        return []  # shouldn't get here

    def compareResults(self, sourceCount, targetCount):
        """Source-to-target comparison of dict keys and values.

        Args:
            sourceCount (dict): source dictionary with source strings as keys
            and frequency as value.
            targetCount (dict): target dictionary with target strings as keys
            and frequency as value.
        """
        badResults = []

        for key, value in sourceCount.items():
            if value != targetCount[key]:
                badResult = "ERROR: %s: %s VS %s\n" % (key, value, targetCount[key])
                badResults.append(badResult)
            else:
                self.outputfile.write("No error: %s\n" % (key))  # good result

        for error in badResults:
            self.outputfile.write(error)

    def isChineseChar(self, char):
        """Check to see if current char is a Chinese character."""
        # Trick by Ceshine Lee
        return True if (re.search("[\u4e00-\u9FFF]", char)) else False

    def getNumbers(self, source, target):
        """Retrieves numbers from both source and target strings, returning count
        dictionaries.

        Args:
            source (string): source string with chinese punctuation removed.
            target (string): target string.

        Returns:
            tuple: entry 1: dictionary with source nums / frequencies as key/value pairs.
                    entry 2: dict with target nums / frequences as key/value pairs.
        """

        sourceCount = defaultdict(int)
        targetCount = defaultdict(int)

        DIGITNUMBER = r"[^.\dA-Z]([\d]+(?:[.][\d]+)*)"
        NODIGIT = r"\D([.][\d]+)"

        sourceResult = re.findall(DIGITNUMBER, source) + re.findall(NODIGIT, source)

        for num in sourceResult:
            if num != "..":
                sourceCount[num] += 1

        targetResult = re.findall(DIGITNUMBER, target) + re.findall(NODIGIT, target)
        for num in targetResult:
            if num != "..":
                targetCount[num] += 1

        return sourceCount, targetCount
