import DatabaseHelper
import unittest
import PhraseLoader
import XLIFFParser2
import FileReader
import ExtractContent
import Validator
import os
import sys
import ReferenceNumberCounter

from collections import defaultdict

# TODO: update outdated tests below

class TestExtractContent(unittest.TestCase):
    def setUp(self):
        testfile = "./TestFiles/testDir/testsdlxlifffile.sdlxliff"
        parser = XLIFFParser2.XMLParser(testfile)
        self.parsedTree = parser.run()
        parser.closeFile()
        self.extractor = ExtractContent.TagBinder(self.parsedTree)

    def testFindIPCCode(self):
        IPCCODE = self.extractor.findIPCCode()
        self.assertTrue(IPCCODE[0] == "G02B")
        self.assertTrue(IPCCODE[1] == "13/00")

    def testTreeDict(self):
        """only tests to see if tree dict is being correctly populated"""
        self.assertTrue("st" in self.extractor.dataTree)
        self.assertTrue("source" in self.extractor.dataTree)
        self.assertTrue("target" in self.extractor.dataTree)
        self.assertTrue("seg-source" in self.extractor.dataTree)

        # TODO: dfs source/target tests. Must create simpler test file to
        # validate the DFS logic


class TestLoader(unittest.TestCase):
    def setUp(self):
        self.loader = PhraseLoader.TermLoader("./TestFiles/PhraseLoaderTest.test")

    def testComment(self):
        self.assertTrue(self.loader.isComment("# "))
        self.assertFalse(self.loader.isComment("t "))
        self.loader.closeFiles()

    def testWellFormatted(self):
        self.assertTrue(self.loader.wellFormatted("吃饭, eat food"))
        self.assertFalse(self.loader.wellFormatted("吃饭 eat food"))
        self.loader.closeFiles()

    def testRemoveSpace(self):
        self.assertTrue(" " not in self.loader.removeSpace(" I am cool  "))
        self.loader.closeFiles()

    def testCleanSplit(self):
        src, tgt = self.loader.cleanSplit("吃饭, eat food")
        self.assertTrue(
            src[0]
            in (
                "吃",
                "饭",
            )
        )
        self.assertTrue(tgt == (("eat", "food")))
        self.loader.closeFiles()

    @unittest.skip("")
    def testRemoveChineseMarkings(self):
        pass

    def testLoadTerms(self):
        self.loader.loadTerms()
        db, ndb = self.loader.getTermDicts()
        self.assertTrue(
            (
                "静",
                "脉",
            )
            in db
        )
        self.assertTrue(
            (
                "权",
                "利",
                "要",
                "求",
            )
            in ndb
        )
        self.loader.closeFiles()

    def testIsDatabaseFlag(self):
        self.assertTrue(self.loader.isDatabaseFlag("@@@"))
        self.assertTrue(self.loader.isDatabaseFlag("@@@ "))
        self.assertFalse(self.loader.isDatabaseFlag("@@@.. "))
        self.loader.closeFiles()


class testFileReader(unittest.TestCase):
    """Simple EOF/Readin Test"""

    def setUp(self):
        testfile = open("./TestFiles/FileReaderTest.test", "w")
        testfile.write("THIS IS A TEST")
        testfile.close()
        self.reader = FileReader.FileReader("./TestFiles/FileReaderTest.test")

    def testRead(self):
        string = ""
        while True:
            output = self.reader.getNextChar()
            if not output:
                break
            string += output
        self.assertTrue(string == "THIS IS A TEST")


@unittest.skip("")
class testXMLParser(unittest.TestCase):
    def setUp(self):
        self.parser = XLIFFParser2.XMLParser("TestXMLParser.xml")

    def testGetNextChar(self):
        self.assertEqual("<", self.parser.getNextChar())
        self.parser.closeFile()

    def testGetNextString(self):
        self.parser.getNextChar()
        self.assertEqual("?xml", self.parser.getNextString())
        self.assertEqual('version="1.0"', self.parser.getNextString())
        self.parser.closeFile()

    def testFindNextTag(self):
        self.assertEqual(self.parser.getNextTag(), "?xml")
        self.assertEqual(self.parser.getNextTag(), "xliff")
        self.assertEqual(self.parser.getNextTag(), "seg-source")
        self.parser.closeFile()

    def testGetTagAttributes(self):
        self.parser.getNextTag()
        self.parser.closeFile()

    @unittest.skip("")
    def testGetTagTree(self):
        print("----------------")
        tag = self.parser.getNextTag()
        while tag != "seg-source":
            tag = self.parser.getNextTag()
        k = self.parser.getTagTree(tag)
        self.parser.closeFile()

    @unittest.skip("")
    def testParser(self):
        print("----------------")
        data = self.parser.run()
        self.parser.closeFile()
        print(data)

    def testRealFile(self):
        newParser = XLIFFParser2.XMLParser("pctcn2020.xml")
        data = newParser.run()
        self.parser.closeFile()
        newParser.closeFile()


class testValidator(unittest.TestCase):
    def setUp(self):
        parsedList = [["TESTPATH", "静脉狭小。", "narrow vein."]]
        termDict = {("静", "脉"): [("vein",)]}
        self.outputDoc = open("./TestFiles/outputtest.test", "w+")
        self.validator = Validator.Validator(termDict, self.outputDoc, parsedList)

    def testExtractTerms(self):

        for entry in self.validator.parsedList:
            ID, source, target = entry

            sourceDict = defaultdict(int)
            targetDict = defaultdict(int)

            self.validator.extractTerms(
                source, self.validator.sourceDict, 1, sourceDict, "ZH"
            )

            self.assertTrue(len(sourceDict) == 0)

            self.validator.extractTerms(
                source, self.validator.sourceDict, 2, sourceDict, "ZH"
            )

            self.assertTrue(len(sourceDict) == 1)

            self.validator.extractTerms(
                target, self.validator.targetDict, 1, targetDict, "EN"
            )

            self.assertTrue(len(targetDict) == 1)

            self.validator.extractTerms(
                target, self.validator.targetDict, 2, targetDict, "EN"
            )
            self.assertTrue(len(targetDict) == 1)
            self.outputDoc.close()

    def testreplaceChinesePunctuation(self):
        string = "我的玛雅。我和/或你都“喜欢”(聊天)！"
        self.assertEqual(
            self.validator.replaceChinesePunctuation(string), '我的玛雅.我和/或你都"喜欢"(聊天)!'
        )
        self.outputDoc.close()

    def testRemoveCharacters(self):
        string1 = '我的玛雅.我和/或你都"喜欢"(聊天)!'
        string2 = "my dog's aunt/uncle sorta-kinda like fish."
        print(self.validator.removePunctuation(string1))
        print(self.validator.removePunctuation(string2))


class TestReferenceCounter(unittest.TestCase):
    def setUp(self):
        idnum = "1.TEST"
        source = "(S02)是推杆, (S03)也是推杆, (S06,S05)也都是推杆! 1.11, 2.2, 300mg"
        target = "(S02) is a push rod, (S03) is a push rod, (S04, S05) are both push rods. 1.11, 2.22, 300mg."

        matches = [(idnum, source, target)]
        testFile = open("./TestFiles/test_ref_file.test", "w")
        self.rfcounter = ReferenceNumberCounter.CompareReferenceElements(
            matches, testFile
        )

    def testIsChineseChar(self):
        self.assertTrue(self.rfcounter.isChineseChar("的"))
        self.assertFalse(self.rfcounter.isChineseChar("A"))

    @unittest.skip("")
    def testGetNumbers(self):
        sourceNumbers = "杯子的容量为500ml, 体量是1.54kg. 100,300,5..1"
        targetNumbers = "the cup can hold 500ml and weighs 1.54kg. 100, 300, 5. .1"

        # self.assertTrue(self.rfcounter.compareResults(self.rfcounter.getNumbers(sourceNumbers, targetNumbers) == []))

        sourceNumbers = "杯子的容量为50ml, 体量是1.24kg. 100、300、5..10"
        targetNumbers = "the cup can hold 500ml and weighs 1.54kg. 100, 300, 5. .1"

        # badRes = self.rfcounter.getNumbers(sourceNumbers, targetNumbers)

        self.assertTrue(badRes[0][0] == "50")
        self.assertTrue(badRes[1][0] == "1.24")
        self.assertTrue(badRes[2][0] == ".10")

    def testGetElements(self):
        test1 = ["(S02)是推杆", 1]
        test2 = ["(S02, S03)是两种推杆", 1]
        test3 = ["(S02, S03相当于S04)是两种推杆", 1]  # should fail
        test4 = ["(是两种推杆)", 1]  # should fail

        self.rfcounter.curState = test1
        self.assertEqual((self.rfcounter.getSourceElements()), ["S02"])

        self.rfcounter.curState = test2
        self.assertEqual((self.rfcounter.getSourceElements()), ["S02", "S03"])

        self.rfcounter.curState = test3
        self.assertEqual((self.rfcounter.getSourceElements()), [])

        self.rfcounter.curState = test4
        self.assertEqual((self.rfcounter.getSourceElements()), [])

        self.rfcounter.closeOutputFile()

    def testGetTargetElements(self):
        test1 = ["(S02) is a push rod.", 1]
        test2 = ["(S02, S03) are push rods.", 1]
        test3 = ["(S02, S03, and other junk) are push rods.", 1]
        test4 = ["(JUNK JUNK JUNK)", 1]

        self.rfcounter.curState = test1
        self.assertEqual((self.rfcounter.getSourceElements()), ["S02"])

        self.rfcounter.curState = test2
        self.assertEqual((self.rfcounter.getSourceElements()), ["S02", "S03"])

        self.rfcounter.curState = test3
        self.assertEqual(self.rfcounter.getSourceElements()[4], "junk")

        self.rfcounter.curState = test4
        self.assertEqual(self.rfcounter.getSourceElements()[2], "JUNK")
        self.rfcounter.closeOutputFile()

    def testGetSourceFigNumbers(self):
        source = "(S02)是推杆, (S03)也是推杆, (S04,S05)也都是推杆!"
        source = "(S02)是推杆, (S03)也是推杆, (S04,S05)也都是推杆!(这不是好东西)"
        self.rfcounter.closeOutputFile()
        print(self.rfcounter.getSourceFigNumbers(source))

    def testCompareResults(self):
        sourceDict = {"1.11": 2, "1.21": 1}
        targetDict = {"1.11": 1, "1.21": 1}

        self.rfcounter.compareResults(sourceDict, targetDict)
        self.rfcounter.closeOutputFile()

    def testCompareTexts(self):
        self.rfcounter.compareTexts()

        self.rfcounter.closeOutputFile()
        print(open("./TestFiles/test_ref_file.test", "r").read())


def deleteTestFiles():
    try:
        os.remove("FileReaderTest.test")
        os.remove("PhraseLoaderTest.test")
    except:
        print("No test files were deleted.  No test file loaded?")


if __name__ == "__main__":
    unittest.main()
    deleteTestFiles()
