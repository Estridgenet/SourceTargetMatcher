### Name: Eli Estridge
### Date: 3 APR 2021
### Use: Patent Phrase Validator
import sys

import PhraseLoader
import XLIFFParser2
import ExtractContent
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
            self.writeResults(ID, results)

    def extractTerms(self, string, terms, matchLength, countDict, lang):

        if lang == "ZH":
            words = string.rstrip()
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

    def compareCounts(self, sourceCount, targetCount):

        results = deque()

        for sourceWord, targetWord in self.sourceDict.items():

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
        """only works for 1-1 correspondences"""
        invertedDict = dict()
        for k, v in d.items():
            invertedDict[v] = k
        return invertedDict

    def removePunctuation(self, word):

        if word[0] in self.punctuationSet:
            word = word[1:]

        if word[-1] in self.punctuationSet:
            word = word[0 : len(word) - 1]

        return word


def main(termsList, xliffFile):

    output = open("output.txt", "w+")

    termLoader = PhraseLoader.TermLoader(termsList)
    termLoader.loadTerms()
    termDict = termLoader.getTermDict()

    parser = XLIFFParser2.XMLParser(xliffFile)
    parsedTree = parser.run()
    print(parsedTree)
    extractor = ExtractContent.TagBinder(parsedTree)

    # For SDLXLIFF Files
    matchList = extractor.findSourceTargetMatch("seg-source", "target")

    # For XLIFF Files
    # TODO: add XLIFF functionality!
    matchList += extractor.findSourceTargetMatch("source", "target")

    k = Validator(termDict, output, matchList)
    k.run()

    output.close()


if __name__ == "__main__":
    termsList = sys.argv[1]
    xliffFile = sys.argv[2]
    main(termsList, xliffFile)
