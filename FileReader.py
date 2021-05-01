import sys


class FileReader:
    """Character by character File Reader.

    Args:
        file path (str): file path of source .xliff or .sdlxliff document.
    """

    def __init__(self, f):
        try:
            self.file = open(f, "r", encoding="utf-8")
        except IOError:
            sys.stderr.write("File read error, please check directory path")
            raise IOError

        self.state = None
        self.readNextLine()  # initialize state

    def closeFile(self):
        """Closes the file being read."""
        self.file.close()

    def readNextLine(self):
        """Saves the next line as the current state."""
        self.state = [self.getNextLine(), 0]

    def getNextLine(self):
        """Reads the next line from the file as a string."""

        line = self.file.readline()
        return line

    def getNextChar(self):
        """Returns next character from the file.

        Returns:
            The next character that is not a tab, a newline, or a carriage feed.
            If EOF, returns the empty string.
        """

        # Load new line when old line is exhausted
        if len(self.state[0]) == self.state[1]:
            self.readNextLine()

        if self.state[0] == "":
            self.closeFile()
            return ""  # EOF

        output = self.state[0][self.state[1]]
        self.state[1] += 1  # state change

        # recurse if no suitable char is found, will break if you give it
        #  data with 1000+ newlines
        if output in ("\t", "\r", "\n"):
            return self.getNextChar()

        return output
