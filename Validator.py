import PhraseLoader
import ReferenceNumberCounter
import XLIFFParser2
import ExtractContent
import DatabaseHelper as db

import sys
import re
from collections import deque
from collections import defaultdict

# TODO: Add documentation/improve readability


"""This is a multi-pass validator to check for missed terminology and
mistranslated phrases in the segments of a patent.

The design is as follows: there are 3 files, a standard terminology
document supplied by me, the creator (which includes patent-related terms, though the document 
fully editable by the user), a specific terminology file (e.g. document-specific term file) provided by the user, and an XLIFF or 
SDLXLIFF document.

The latter two (specific term UTF-8 encoded file and xliff/sdlxliff file) are given on the command line in the given format: 
    python Validator.py USERTERMBASE.txt USERXLIFFFILE.XLIFF

An output file is written as output.txt once the file has completed.

"""


class Validator:
    def __init__(self, termDict, outputDoc, parsedList):
        self.parsedList = parsedList
        self.sourceDict = termDict
        self.targetDict = self.invertDict(
            self.sourceDict
        )  # For target-to-source lookup
        self.outputDoc = outputDoc
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
            "。": ".",
            "！": "!",
            "《": "<",
            "》": ">",
        }

    def run(self):
        wordResults = []

        for entry in self.parsedList:
            ID, sourceSegment, targetSegment = entry

            sourceCount = defaultdict(int)
            targetCount = defaultdict(int)

            # Grab matching strings of length 1 to 10
            for stringLength in range(1, 10):
                self.extractTerms(
                    sourceSegment, self.sourceDict, stringLength, sourceCount, "ZH"
                )
                self.extractTerms(
                    targetSegment, self.targetDict, stringLength, targetCount, "EN"
                )

            results = self.compareCounts(sourceCount, targetCount)

            wordResults.append([ID, results])

        return wordResults

    def extractTerms(self, string, terms, matchLength, countDict, lang):
        """removes unnecessary punctuation and creates a list from the terms"""

        if lang == "ZH":
            words = list(
                filter(
                    lambda x: x != "",
                    map(
                        self.removePunctuation,
                        [
                            i
                            for i in self.replaceChinesePunctuation(
                                string.lower()
                            ).rstrip()
                        ],
                    ),
                )
            )

        elif lang == "EN":
            words = list(
                filter(
                    lambda x: x != "",
                    map(
                        self.removePunctuation,
                        re.sub("[%-/]", " ", string.rstrip().lower()).split(" "),
                    ),
                )
            )

        for sliceStart in range(0, len(words) - (matchLength - 1)):

            if lang == "ZH":
                stringSlice = tuple(words[sliceStart : sliceStart + matchLength])

            elif lang == "EN":
                stringSlice = tuple(
                    words[sliceStart : sliceStart + matchLength],
                )

            if stringSlice in terms:
                countDict[stringSlice] += 1

    def replaceChinesePunctuation(self, string):
        return "".join(
            [i if i not in self.replaceDict else self.replaceDict[i] for i in string]
        )

    def compareCounts(self, sourceCount, targetCount):

        results = deque()

        for sourceWord, targetList in self.sourceDict.items():
            # print("####")
            # print(sourceWord, targetList)
            swCount = sourceCount[sourceWord]
            twCount = 0

            # The following compares the count of ALL words attached to the source word
            # Therefore, if a single source word is attached to many target words, it
            # will add up the frequency of ALL target words and compare it to the frequency
            # of the source
            for targetWord in targetList:

                twCount += targetCount[targetWord]

            if swCount != twCount:
                badResult = (
                    "###\nPlease check the following phrase:\n%s: %d, %s: %d\n###\n"
                    % (
                        sourceWord,
                        swCount,
                        targetWord,
                        twCount,
                    )
                )
                results.append(badResult)

            else:
                goodResult = "No error:  %s: %d, %s: %d\n" % (
                    sourceWord,
                    swCount,
                    targetWord,
                    twCount,
                )
                results.appendleft(goodResult)

        return results

    def writeResults(self, wordRes, refRes, numRes):
        VERBOSE = False
        for i in range(len(wordRes)):
            ID = wordRes[i][0]
            self.outputDoc.write("Segment ID: %s\n" % (ID))
            self.outputDoc.write("Word Results:\n")
            for entry in wordRes[i][1]:
                if VERBOSE is False and entry.startswith('No error'):
                    continue
                self.outputDoc.write(entry)
            self.outputDoc.write("\nRef Num Results:\n")
            for entry in refRes[i][1]:
                if VERBOSE is False and entry.startswith('No error'):
                    continue
                self.outputDoc.write(entry)
            self.outputDoc.write("\nNumber Results:\n")
            for entry in numRes[i][1]:
                if VERBOSE is False and entry.startswith('No error'):
                    continue
                self.outputDoc.write(entry)
            self.outputDoc.write("\n#####################\n")

    def invertDict(self, d):
        """only works for 1-k correspondences"""
        invertedDict = dict()
        for k, vList in d.items():
            for v in vList:
                invertedDict[v] = k
        return invertedDict

    def removePunctuation(self, word):

        return "".join([char for char in word if char not in self.punctuationSet])


def getFileDir(filepath):

    for curIndex in range(len(filepath) - 1, -1, -1):
        if filepath[curIndex] == "/" or filepath[curIndex] == "\\":
            break
    if curIndex != 0:
        return filepath[0 : curIndex + 1]
    return ""


def main(termsList, xliffFile):

    # Loads terms List into Term Loader
    termLoader = PhraseLoader.TermLoader(termsList)
    termLoader.loadTerms()

    # Grabs Terms to be saved and terms not being saved in database
    specTermDictForDatabase, specTermDictNoSave = termLoader.getTermDicts()
    database = db.DatabaseHelper()

    # Parses xliff file into a list of trees
    parser = XLIFFParser2.XMLParser(xliffFile)
    parsedTree = parser.run()

    # Grabs content pairs
    extractor = ExtractContent.TagBinder(parsedTree)
    IPCCODEGENERIC, IPCODESPECIFIC = extractor.findIPCCode()

    # Fetches relevant IPC Code terms from database
    genTermDict = database.getTerms(IPCCODEGENERIC)

    # creates output file in same directory as the xliff file
    output = open(getFileDir(xliffFile) + "output_check.txt", "w+")

    # For SDLXLIFF Files
    matchList = extractor.findSourceTargetMatch("seg-source", "target")

    # For XLIFF Files
    # TODO: add XLIFF functionality
    # matchList += extractor.findSourceTargetMatch("source", "target")

    # Runs check
    k = Validator(
        {**genTermDict, **specTermDictForDatabase, **specTermDictNoSave},
        output,
        matchList,
    )
    phraseResults = k.run()

    # Runs reference tag check
    refChecker = ReferenceNumberCounter.CompareReferenceElements(matchList, output)
    refResults, numResults = refChecker.compareTexts()

    # Write output file
    k.writeResults(phraseResults, refResults, numResults)

    # add relevant terms to dictionary and rewrite to database
    database.setTerms(specTermDictForDatabase, IPCCODEGENERIC)
    database.updateDatabase()

    output.close()


if __name__ == "__main__":
    termsList = sys.argv[1]
    xliffFile = sys.argv[2]
    main(termsList, xliffFile)
