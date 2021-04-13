import FileReader
import itertools

counter = itertools.count()


class Node:
    def __init__(self, tag):
        self.TAGID = next(counter)

        self.tag = tag
        self.parent = None
        self.attributes = dict()
        self.children = []
        self.content = []

    def __repr__(self):
        stringID = "Node %i\n" % (self.TAGID)
        stringTag = "Tag: %s\n" % (self.tag)
        stringAttributes = repr(self.attributes) + "\n"

        stringChildren = "Children:\n"
        for child in self.children:
            stringChildren += child.tag + " "

        stringChildren += "\n"

        dataz = "".join(["Data:\n"] + [i for i in self.content])

        return stringID + stringTag + stringAttributes + stringChildren + dataz

    def __str__(self):
        return self.__repr__()


class XMLParser:
    def __init__(self, xmlDoc, searchTags=None):
        self.reader = FileReader.FileReader(xmlDoc)
        self.ILLEGALCHARS = set(["\t", "\n"])

        if searchTags:
            self.searchTags = searchTags  # how should we do these?
        else:
            self.searchTags = set(
                ["seg-source", "mrk", "target"]
            )  # necessary source tags for SDL XLIFF

        self.tagStack = []  # keep track of embedded tags
        self.charBuffer = ""  # remembers tag enders and attribute enders

    def getNextChar(self):

        # Retrieve an already read-in but unused char
        if self.charBuffer != "":
            output = self.charBuffer
            self.charBuffer = ""

        # Get next valid char from file
        else:
            output = self.reader.getNextChar()
            while output in self.ILLEGALCHARS:
                output = self.reader.getNextChar()
        return output

    def getNextString(self):
        output = []

        self.charBuffer = ""
        curChar = self.getNextChar()

        while curChar not in (" ", ">"):
            output.append(curChar)
            curChar = self.getNextChar()

        self.charBuffer = curChar
        return "".join(output)

    def getNextTag(self):

        output = self.getNextChar()
        while output != "" and output != "<":  # scan for XML tag opener, end at EOF
            output = self.getNextChar()

        if output == "":
            return None  # EOF

        tag = self.getNextString()
        return tag

    def getTagTree(self, tag):

        dataFragment = Node(tag)

        self.tagStack.append(tag)
        thisTagID = (tag, len(self.tagStack))  # remembers place in tag stack

        attributes, endOfTag = self.getTagAttributes()

        if len(attributes) != 0:
            dataFragment.attributes = attributes

        if endOfTag:
            self.tagStack.pop()

        else:
            while thisTagID[1] <= len(self.tagStack):

                content = self.getContent()
                if content != "":
                    dataFragment.content.append(content)

                subTree = self.getSubTree()
                if subTree:
                    subTree.parent = dataFragment
                    dataFragment.children.append(subTree)

        return dataFragment

    def getSubTree(self):
        tag = self.getNextTag()
        if self.isClosingTag(tag):
            _ = self.getNextChar()
            self.tagStack.pop()
            return None
        return self.getTagTree(tag)

    def getTagAttributes(self):

        tagData = dict()

        curChar = self.getNextChar()
        while curChar not in (
            ">",
            "/",
        ):

            attID = self.getAttributeID()
            attValue = self.getAttributeValue()

            tagData[attID] = attValue
            curChar = self.getNextChar()

        if curChar in ("/"):
            _ = self.getNextChar()
            return tagData, True  # End of Tag
        return tagData, False

    def removeSpace(self):

        curChar = self.getNextChar()
        while curChar == " ":
            curChar = self.getNextChar()
        self.charBuffer = curChar

    def getAttributeID(self):
        self.removeSpace()

        attributeID = []
        curChar = self.getNextChar()
        while curChar != "=":
            attributeID.append(curChar)
            curChar = self.getNextChar()

        return "".join(attributeID)

    def getAttributeValue(self):
        _ = self.getNextChar()  # First '"'

        attributeValue = []
        curChar = self.getNextChar()
        while curChar != '"':
            attributeValue.append(curChar)
            curChar = self.getNextChar()

        return "".join(attributeValue)

    def getContent(self):
        contentString = []
        curChar = self.getNextChar()
        while curChar != "<":
            contentString.append(curChar)
            curChar = self.getNextChar()

        self.charBuffer = curChar

        return "".join(contentString)

    def isClosingTag(self, tag):
        return tag[0] == "/"

    def isComment(self):
        return curChar == "!"

    def closeFile(self):
        self.reader.closeFile()

    def run(self):
        dataTree = []
        while True:
            nextTag = self.getNextTag()
            if not nextTag:
                break
            if nextTag in self.searchTags:
                dataTree.append(self.getTagTree(nextTag))

        self.closeFile()

        return dataTree
