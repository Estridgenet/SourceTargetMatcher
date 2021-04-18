# Looks  through all subdirectories in a designated directory and
# pulls the first sdlxliff file and paired termbase file (notes.txt)
# if it can.  If it doesn't find a termbase.txt file OR a .sdlxliff file, it
# continues to next dir without adding any of the files in the current dir
import os
import re


# TODO: Completely redo this terrible GUI

FILETYPEMATCH = ".*?[.]sdlxliff"


def findSDLXLF(files):
    """matches .sdlxliff suffix against files in cur directory"""
    for f in files:
        if re.match(FILETYPEMATCH, f):
            return f
    return None


EXACTFILEMATCH = ".*notes[.]txt"


def findNotes(files):
    """matches notes.txt name against names in cur directory"""
    for f in files:
        if re.match(EXACTFILEMATCH, f):
            return f
    return None


def walkFullDir(directorypath):
    """walks through the directory path in a dfs-like fashion. from top to bottom"""
    filePairs = []
    for root, dirs, files in os.walk(directorypath):

        a = findNotes(files)
        b = findSDLXLF(files)

        if a and b:
            filePairs.append((os.path.join(root, a), os.path.join(root, b)))

    return filePairs


def walkShallowDir(directorypath):
    """walks 1-deep through the directory path"""
    directories = []

    k = os.scandir(directorypath)
    # Get paths of first subdirectories in dirpath
    for node in k:
        if node.is_dir():
            directories.append(node.path)

    filePairs = []

    # scan subdirectories for files
    for subdir in directories:

        files = [i.path for i in os.scandir(subdir) if i.is_file()]

        a = findNotes(files)
        b = findSDLXLF(files)

        if a and b:
            filePairs.append((os.path.join(subdir, a), os.path.join(subdir, b)))

    return filePairs
