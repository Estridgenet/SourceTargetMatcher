import unittest
import PhraseLoader
import XLIFFParser2
import FileReader
import ExtractContent
import os
import sys


class TestLoader(unittest.TestCase):
    def setUp(self):
        testfile = open("PhraseLoaderTest.test", "w")
        testfile.write("")
        testfile.close()
        self.loader = PhraseLoader.TermLoader("PhraseLoaderTest.test")

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
        self.assertTrue(src[0] in ("吃饭",))
        self.assertTrue(tgt == (("eat", "food")))
        self.loader.closeFiles()

    def testLoadTerms(self):
        self.loader.loadTerms()
        k = self.loader.getTermDict()
        print("###")
        for key, val in k.items():
            print(key, val)
        print("###")


class testFileReader(unittest.TestCase):
    def setUp(self):
        testfile = open("FileReaderTest.test", "w")
        testfile.write("THIS IS A TEST")
        testfile.close()
        self.reader = XLIFFParser2.FileReader("FileReaderTest.test")

    def testRead(self):
        string = ""
        while True:
            output = self.reader.getNextChar()
            if not output:
                break
            string += output
        self.assertTrue(string == "THIS IS A TEST")


class testFileReader(unittest.TestCase):
    """Just testing whether it can output and send EOF
    properly"""

    def setUp(self):
        testfile = open("FileReaderTest.test", "w")
        testfile.write("THIS IS A TEST")
        testfile.close()
        self.reader = FileReader.FileReader("FileReaderTest.test")

    def testRead(self):
        string = ""
        while True:
            output = self.reader.getNextChar()
            if not output:
                break
            string += output
        self.assertTrue(string == "THIS IS A TEST")


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
        # print(self.parser.getTagAttributes())
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


class testTagBinder(unittest.TestCase):
    def setUp(self):
        parser = XLIFFParser2.XMLParser("pctcn2020.xml")
        tree = parser.run()
        parser.closeFile()
        self.TagBinder = ExtractContent.TagBinder(tree)

    def testFindSOurceTargetMatch(self):
        self.TagBinder.findSourceTargetMatch("seg-source", "target")


def deleteTestFiles():
    try:
        os.remove("FileReaderTest.test")
        os.remove("PhraseLoaderTest.test")
    except:
        print("Error. No test file loaded?")


if __name__ == "__main__":
    unittest.main()

    deleteTestFiles()
