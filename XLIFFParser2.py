import FileReader
import itertools

COUNTER = itertools.count()

# TODO: comment ignoring
# TODO: <?xml   ?> ignoring (might break parser currently)


class Node:
    def __init__(self, tag):

        self.TAGID = next(COUNTER)
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

        contentString = "".join(["Data:\n"] + [i for i in self.content])

        return stringID + stringTag + stringAttributes + stringChildren + contentString

    def __str__(self):
        return self.__repr__()


class XMLParser:
    def __init__(self, xmlDoc, searchTags=None):

        self.reader = FileReader.FileReader(xmlDoc)

        self.ILLEGALCHARS = set(["\t", "\n", "\r"])

        if searchTags:
            self.searchTags = searchTags  # user specified search tags

        else:
            self.searchTags = set(
                ["seg-source", "mrk", "target", "trans-unit", "source"]
            )  # necessary source tags to find SDLXLIFF and XLIFF source/target segs

        self.tagStack = []  # keep track of embedded tag tree

        self.charBuffer = ""  # for keeping track of '>' and '<' and '/' once char has been read in from file reader

    def getNextChar(self):

        # Retrieve an already read-in but unused char
        if self.charBuffer != "":
            output = self.charBuffer
            self.charBuffer = ""

        # Get next valid char from reader
        else:
            output = self.reader.getNextChar()
            while output in self.ILLEGALCHARS:
                output = self.reader.getNextChar()

        return output

    def getTagName(self):

        output = []
        self.charBuffer = ""  # clear charBuffer in case of '<' or '>'
        curChar = self.getNextChar()

        # reads until beginning of attributes " " or at end of tag ">"

        while curChar not in (
            " ",
            ">",
        ):
            output.append(curChar)
            curChar = self.getNextChar()

        self.charBuffer = curChar  # rebuffer ">" or " "

        return "".join(output)

    def getNextTag(self):

        curChar = self.getNextChar()

        # Scans for XML tag opener, or ends at EOF and returns None
        while curChar != "" and curChar != "<":
            curChar = self.getNextChar()

        if curChar == "":
            return None  # EOF

        return self.getTagName()

    def getTagTree(self, tag):
        if self.isEmptyTag(tag):
            _ = self.getNextChar()
            return

        # Create new node for current tag and read in attributes and relevant content
        root = Node(tag)

        self.tagStack.append(tag)

        # remembers position in tag stack, will stop recursively finding subTags once this tag is
        # popped from stack

        TagID = (tag, len(self.tagStack))

        attributes, endOfTag = self.getTagAttributes()

        if len(attributes) != 0:
            root.attributes = attributes

        if endOfTag:
            self.tagStack.pop()

        else:
            while TagID[1] <= len(self.tagStack):

                content = self.getContent()
                if content != "":
                    root.content.append(content)

                subTree = self.getSubTree()
                if subTree:
                    subTree.parent = root
                    root.children.append(subTree)

        print(root)
        return root

    def getSubTree(self):
        tag = self.getNextTag()

        # if next tag is closing tag for given tree, end search for subtree
        if self.isClosingTag(tag):
            _ = self.getNextChar()  # clear ">"
            self.tagStack.pop()
            return None

        return self.getTagTree(tag)

    def getTagAttributes(self):

        tagAttributeData = dict()

        curChar = self.getNextChar()
        while curChar not in (
            ">",
            "/",
        ):

            attID = self.getAttributeID()
            attValue = self.getAttributeValue()

            tagAttributeData[attID] = attValue
            curChar = self.getNextChar()

        if curChar in ("/"):
            _ = self.getNextChar()  # clear ">"

            return tagAttributeData, True  # End of Tag

        return tagAttributeData, False

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

        self.charBuffer = curChar  # re-add "<"

        return "".join(contentString)

    def isClosingTag(self, tag):
        return tag[0] == "/"

    def isEmptyTag(self, tag):
        return tag[-1] == "/"

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
