class XLIFFParser:
    def __init__(self, xliffDoc, outputDoc):
        self.xliffDoc = open(xliffDoc, "r")
        self.outputDoc = outputDoc
        self.intermedParseDoc = open("parsedoc.int", "w+")

    def getNextLine(self):
        return self.xliffDoc.readline().rstrip()

    def writeMetaData(self):
        self.outputDoc.write("FILE METADATA\n")
        nextLine = self.getNextLine()
        while nextLine != "<body>":
            self.outputDoc.write(nextLine + "\n")
            nextLine = self.getNextLine()

    def getID(self, line):
        return line[line.index("=") + 1 : len(line) - 1]

    def getSource(self):
        """currently doesn't handle muliple lines.  Expects single lines"""
        line = self.getNextLine()
        return line[8 : len(line) - 9]

    def getTarget(self):
        line = self.getNextLine()
        return line[8 : len(line) - 9]

    def readBody(self):

        nextLine = self.getNextLine()
        while nextLine != "</body>":
            self.intermedParseDoc.write(self.getID(nextLine) + ",")
            self.intermedParseDoc.write(self.getSource() + ",")
            self.intermedParseDoc.write(self.getTarget() + "\n")

            # yield [self.getID(nextline), self.getSource(), self.getTarget()]

            _ = self.getNextLine()
            while _ != "</trans-unit>":  # skip all intermediate junk
                _ = self.getNextLine()

            nextLine = self.getNextLine()

    def closeFile(self):
        self.xliffDoc.close()
        self.intermedParseDoc.close()

    def run(self):
        self.writeMetaData()
        self.readBody()
        self.closeFile()

# for testing
def main():
    output = open('output.txt', 'w+')
    xlParse = XLIFFParser('testfile.xliff', output)
    xlParse.run()

