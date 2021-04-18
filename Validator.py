### Name: Eli Estridge
### Date: 3 APR 2021
### Use: Patent Phrase Validator
import sys

import PhraseLoader
import XLIFFParser2
import ExtractContent
import DatabaseHelper as db
from collections import deque

from collections import defaultdict

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
            [",", ".", "?", ";", "。", "'", '"', "”", "“", "，", "、", "\n"]
        )

    def run(self):

        for entry in self.parsedList:
            ID, sourceSegment, targetSegment = entry

            sourceCount = defaultdict(int)
            targetCount = defaultdict(int)

            for stringLength in range(1, 10):
                self.extractTerms(
                    sourceSegment, self.sourceDict, stringLength, sourceCount, "ZH"
                )
                self.extractTerms(
                    targetSegment, self.targetDict, stringLength, targetCount, "EN"
                )

            results = self.compareCounts(sourceCount, targetCount)
            # print(sourceCount)
            # print(targetCount)

            self.writeResults(ID, results)

    def extractTerms(self, string, terms, matchLength, countDict, lang):

        if lang == "ZH":
            words = self.replaceChinesePunctuation(string.rstrip().lower())
            print(words)
        elif lang == "EN":
            words = list(
                map(self.removePunctuation, string.lower().rstrip().split(" "))
            )

        for sliceStart in range(0, len(string) - (matchLength - 1)):
            if lang == "ZH":
                s = words[sliceStart : sliceStart + matchLength]
                stringSlice = (s,)
            elif lang == "EN":
                stringSlice = tuple(
                    words[sliceStart : sliceStart + matchLength],
                )
            if stringSlice in terms:
                countDict[stringSlice] += 1

    def replaceChinesePunctuation(self, string):
        replaceDict = {"（": "(", "）": ")", "，": ",", "“": '"', "”": '"', "。": "."}
        return "".join([i if i not in replaceDict else replaceDict[i] for i in string])

    def compareCounts(self, sourceCount, targetCount):

        results = deque()

        for sourceWord, targetList in self.sourceDict.items():
            for targetWord in targetList:
                swCount = sourceCount[sourceWord]

                twCount = targetCount[targetWord]

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

    def writeResults(self, ID, results):
        self.outputDoc.write("Segment ID: %s\n" % (ID))
        for r in results:
            self.outputDoc.write(r)
        # self.outputDoc.write("\n")

    def invertDict(self, d):

        # TODO: better 1-k functionality (current processes terms as if they are completely separate)

        """only works for 1-k correspondences"""
        invertedDict = dict()
        for k, vList in d.items():
            for v in vList:
                invertedDict[v] = k
        return invertedDict

    def removePunctuation(self, word):

        if word[0] in self.punctuationSet:
            word = word[1:]

        if word[-1] in self.punctuationSet:
            word = word[0 : len(word) - 1]

        return word


def getFileDir(filepath):

    for curIndex in range(len(filepath) - 1, -1, -1):
        if filepath[curIndex] == "/" or filepath[curIndex] == "\\":
            break
    if curIndex != 0:
        return filepath[0 : curIndex + 1]
    return ""


def main(termsList, xliffFile):

    termLoader = PhraseLoader.TermLoader(termsList)
    termLoader.loadTerms()
    specTermDictForDatabase, specTermDictNoSave = termLoader.getTermDicts()
    database = db.DatabaseHelper()

    parser = XLIFFParser2.XMLParser(xliffFile)
    parsedTree = parser.run()

    extractor = ExtractContent.TagBinder(parsedTree)
    IPCCODE = extractor.findIPCCode()

    # Fetch from database
    genTermDict = database.getTerms(IPCCODE)

    # Update Database
    # DatabaseHelper.addterms(IPCCODE, specificTerms)

    # writes to same directory as the xliff file
    output = open(getFileDir(xliffFile) + "output_check.txt", "w+")

    # For SDLXLIFF Files
    matchList = extractor.findSourceTargetMatch("seg-source", "target")

    # For XLIFF Files
    # TODO: add XLIFF functionality
    # matchList += extractor.findSourceTargetMatch("source", "target")

    k = Validator(
        {**genTermDict, **specTermDictForDatabase, **specTermDictNoSave},
        output,
        matchList,
    )
    k.run()

    # add relevant terms to dictionary
    database.setTerms(specTermDictForDatabase, IPCCODE)
    database.updateDatabase()

    output.close()


if __name__ == "__main__":
    termsList = sys.argv[1]
    xliffFile = sys.argv[2]
    main(termsList, xliffFile)
