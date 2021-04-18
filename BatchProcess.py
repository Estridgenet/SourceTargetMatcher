
# Looks 1 deep through all subdirectories in a designated directory and
# pulls the first (and hopefully only) sdlxliff file and paired termbase file
# if it can.  If it doesn't find a termbase.txt file OR a .sdlxlf file, it
# continues to next dir
import os
import re


FILETYPEMATCH = ".*?[.]sdlxliff"
def findSDLXLF(files):
    for f in files:
        if re.match(FILETYPEMATCH, f):
            return f
    return None

EXACTFILEMATCH = "notes[.]txt"
def findNotes(files):
    for f in files:
        print(f)
        if re.match(EXACTFILEMATCH, f):
            return f
    return None

def walkDir(directorypath):
    filePairs = []
    for root, dirs, files in os.walk(directorypath):

        a = findNotes(files)
        b = findSDLXLF(files)

        if a and b:
            filePairs.append((os.path.join(root, a),os.path.join(root, b)))

    return filePairs




