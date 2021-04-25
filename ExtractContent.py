# Sample SDLXLIFF tagging:
# <target><mrk mtype="seg" mid="5"/></target>
# <seg-source><mrk mtype="seg" mid="5">Drawing_references_to_be_translated:</mrk>

import re

# Sample XLIFF tagging:

# TODO: Cleanup, can probably just use one dfs structure
# TODO: Needs to be compatible with report files

"""
<body>
<trans-unit id="0000000001" datatype="x-text/xml" restype="string">
<source>人机交互系统及其方法、终端设备</source>
<target/>
</trans-unit>
</body>
"""

from collections import defaultdict
import XLIFFParser2


class TagBinder:
    """
    a collection of trees is passed in with nodes.
    Nodes have the following attributes:
    parent: node
    nodeid: int
    tag: string
    attributes: dict
    children: list of nodes
    content: list of strings
    """

    def __init__(self, dataTree):

        self.dataTree = self.getTreeDict(dataTree)
        self.matchDict = dict()

    def getTreeDict(self, treeList):
        """converts a list of Nodes into a dictionary with the root node
        tag id as key and nodes having said tag id as the values
        Input: parsed xliff data tree list
        returns: data tree dictionary
        """

        tagDict = defaultdict(list)

        for node in treeList:
            tagDict[node.tag].append(node)

        return tagDict

    def dfsSource(self, sourceTag):
        dfsDict = dict()
        for sourceNode in self.dataTree[
            sourceTag
        ]:  # this deletes nodes if said nodes don't have unique tag id & attribute structures
            self.dfsSourceHelper("", sourceNode, dfsDict)

        return dfsDict

    def dfsSourceHelper(self, curPath, curNode, treeDict):
        curPath += "/" + curNode.tag

        for attrID, attrVal in curNode.attributes.items():

            curPath += "," + attrID + "=" + attrVal

        if curNode.content:
            treeDict[curPath] = self.stringify(curNode.content)

        for subTree in curNode.children:
            self.dfsSourceHelper(curPath, subTree, treeDict)

        return treeDict

    def dfsTarget(self, sourceDict, sourceTag, targetTag):

        matches = []
        for targetNode in self.dataTree[targetTag]:
            self.dfsTargetFinder("", sourceTag, targetNode, sourceDict, matches)

        return matches

    def dfsTargetFinder(self, curPath, matchTag, curNode, sourceDict, matches):
        if not curPath:
            curPath = "/" + matchTag
        else:
            curPath += "/" + curNode.tag

        for attrID, attrVal in curNode.attributes.items():

            curPath += "," + attrID + "=" + attrVal

        if curNode.content and curPath in sourceDict:
            matches.append(
                [curPath, sourceDict[curPath], self.stringify(curNode.content)]
            )

        for subTree in curNode.children:
            self.dfsTargetFinder(curPath, matchTag, subTree, sourceDict, matches)

    def stringify(self, content):

        string = ""
        for c in content:
            string += c + "\n"
        return string

    def findIPCCode(self):
        """looks for <st> tag within tree, then searches for name="IPC" within
        the content of this is from the original xml file.
        This currently grabs the Generic part (e.g. G02) and specific part (e.g. 13) and returns them as a tuple
        Will return tuple of (None, None) if it finds nothing"""

        for node in self.dataTree["st"]:
            content = self.stringify(node.content)
            if re.search("IPC", content):
                MATCHFINDER = "value=&quot;(.*?)&quot;"
                m = re.search(MATCHFINDER, content).group(1)

                GENERICIPC = r"\w[\d]+[\w]"

                SPECIFICIPC = r"[\d]*[/][\d]*"

                return (
                    re.search(GENERICIPC, m).group()
                    if re.search(GENERICIPC, m)
                    else None,
                    re.search(SPECIFICIPC, m).group()
                    if re.search(SPECIFICIPC, m)
                    else None,
                )

    def findSourceTargetMatch(self, sourceTag, targetTag):
        """this is a rather basic implementation.  It will find
        source / target segments, then compare a subtree path with all
        attributes.  If the subtree path and attributes are EXACTLY the same, then
        content will be pulled from the source / target segments"""
        """Data is returned as a list of sub-lists, the sub-lists being of the form:
        [PATH, SOURCECONTENT, TARGETCONTENT]"""

        sourceDict = self.dfsSource(sourceTag)
        couples = self.dfsTarget(sourceDict, sourceTag, targetTag)

        for c in couples:
            ID, SOURCE, TARGET = c
            # print(ID + "\n" + SOURCE + "\n" + TARGET + "\n")

        return couples
