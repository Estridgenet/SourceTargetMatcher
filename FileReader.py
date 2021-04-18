import sys

class FileReader:

    """Basic State Machine Reader Implementation.  Returns single chars and removes all newline marks.
    Nothing else is removed, but more functionality can be implemented by modifying current
    methods or adding new ones.

    Abstraction: returns chars from input file one at a time.

    Rep Invariant: must input file openable and readable by standard Python open method.
    state is saved in array as curLine string and current position int.

    """

    def __init__(self, f):
        try:
            self.file = open(f, "r")
        except IOError:
            sys.stderr.write("File read error, please check directory path")
            raise IOError

        self.state = None
        self.readNextLine()  # initialize

    def closeFile(self):
        self.file.close()

    def readNextLine(self):
        self.state = [self.getNextLine(), 0]  # TODO: add better buffering capability

    def getNextLine(self):
        return self.file.readline().rstrip()

    def getNextChar(self):

        # Load new line when old line is exhausted
        if len(self.state[0]) == self.state[1]:
            self.readNextLine()

        if self.state[0] == "":
            self.closeFile()
            return ""  # EOF

        output = self.state[0][self.state[1]]
        self.state[1] += 1  # state change

        return output
