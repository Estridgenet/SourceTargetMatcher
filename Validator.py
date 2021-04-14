### Name: Eli Estridge
### Date: 3 APR 2021
### Use: Patent Phrase Validator
import sys

import PhraseLoader
import XLIFFParser2
import ExtractContent
from collections import defaultdict

"""This is a multi-pass validator to check for missed terminology and
mistranslated phrases in the segments of a patent.
The design is as follows: there are 3 files, a standard terminology
document supplied by the creator (and editable by the user), a 
specific terminology file provided by the user, and the segmented 
ZH-EN document."""


class Validator:
    def __init__(self, termDict, outputDoc, parsedList):

        self.parsedList = parsedList
        self.sourceDict = termDict
        self.targetDict = self.invertDict(self.sourceDict)
        self.outputDoc = outputDoc
        self.punctuationSet = set(
            [",", ".", "?", ";", "。", "'", '"', "”", "“", "，", "、","\n"]
        )

    def run(self):
        print (('lens',) in self.targetDict)
        print (('camera') in self.targetDict)

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
            print("RESULTS", results)
            self.writeResults(ID, results)

    def extractTerms(self, string, terms, matchLength, countDict, lang):
        if lang == "ZH":
            words = string
        elif lang == "EN":
            words = list(map(self.removePunctuation, string.split(" ")))

        for sliceStart in range(0, len(string) - (matchLength - 1)):
            if lang == "ZH":
                s = (words[sliceStart:sliceStart+matchLength])
                stringSlice = (s,)
            elif lang == "EN":
                stringSlice = tuple(words[sliceStart : sliceStart + matchLength],)
                if stringSlice == ('lens',):
                    print("HEALFO")
                    print (self.targetDict)
                    if ('lens',) in self.targetDict:
                        print("JESUS FSAHYUI")
                    if stringSlice in self.targetDict:
                        print("FUCK YOU")
            if stringSlice in terms:
                #print('foundSlice', stringSlice)
                countDict[stringSlice] += 1
                if lang == "EN":
                    print('hi')
                    print(countDict)

    def compareCounts(self, sourceCount, targetCount):
        results = []
        for sourceWord, targetWord in self.sourceDict.items():
            swCount = sourceCount[sourceWord]
            twCount = targetCount[targetWord]
            if swCount != twCount:
                badResult = "%s: %d, %s: %d\n" % (
                    sourceWord,
                    swCount,
                    targetWord,
                    twCount,
                )
                results.append(badResult)
        return results

    def writeResults(self, ID, results):
        self.outputDoc.write("Segment ID: %s\n" % (ID))
        for r in results:
            self.outputDoc.write(r)
        self.outputDoc.write("\n")

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


def main():
    termsList = sys.argv[1]
    xliffFile = sys.argv[2]

    output = open("output.txt", "w+")

    termLoader = PhraseLoader.TermLoader(termsList)  # need file
    termLoader.loadTerms()
    termDict = termLoader.getTermDict()

    parser = XLIFFParser2.XMLParser(xliffFile)
    h = ExtractContent.TagBinder(parser.run())  # creates intermediate parsed file
    matchList = h.findSourceTargetMatch("seg-source", "target")

    k = Validator(termDict, output, matchList)
    k.run()

    output.close()


if __name__ == "__main__":
    main()
