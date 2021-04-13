# <target><mrk mtype="seg" mid="5"/></target>
# <seg-source><mrk mtype="seg" mid="5">Drawing_references_to_be_translated:</mrk>
from collections import defaultdict
import XLIFFParser2


class TagBinder:
    """a collections of trees is passed in with nodes.
    Nodes have the following format:
    NODE:
    NODEID: int
    TAG: string
    ATTRIBUTES: dict
    CHILDREN: list of nodes
    CONTENT: list of strings

    """

    def __init__(self, dataTree):
        self.dataTree = self.getTreeDict(dataTree)
        # print(self.dataTree['seg-source'])
        self.matchDict = dict()

    def getTreeDict(self, treeList):
        tagDict = defaultdict(list)
        for node in treeList:
            tagDict[node.tag].append(node)
        return tagDict

    def dfsSource(self, sourceTag):
        dfsDict = dict()
        for sourceNode in self.dataTree[
            sourceTag
        ]:  # THIS WILL DELETE NODES IF THEY DONT HAVE UNIQUE IDS
            self.dfsHelper("", sourceNode, dfsDict)

        return dfsDict

    def dfsHelper(self, curPath, curNode, treeDict):
        curPath += "/" + curNode.tag

        for attrID, attrVal in curNode.attributes.items():

            curPath += "," + attrID + "=" + attrVal

        if curNode.content:
            treeDict[curPath] = self.stringify(curNode.content)

        for subTree in curNode.children:
            self.dfsHelper(curPath, subTree, treeDict)

        return treeDict

    def dfsTarget(self, sourceDict, sourceTag, targetTag):

        matches = []
        for targetNode in self.dataTree[targetTag]:
            self.dfsFinder("", sourceTag, targetNode, sourceDict, matches)

        return matches

    def dfsFinder(self, curPath, matchTag, curNode, sourceDict, matches):
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
            self.dfsFinder(curPath, matchTag, subTree, sourceDict, matches)

    def stringify(self, content):
        string = ""
        for c in content:
            string += c + "\n"
        return string

    def findSourceTargetMatch(self, sourceTag, targetTag):
        """this is a rather basic implementation.  It will find
        source / target segments, then compare a subtree path with all
        attributes.  If the subtree path and attributes are EXACTLY the same, then
        content will be pulled from the source / target segments"""

        sourceDict = self.dfsSource(sourceTag)
        couples = self.dfsTarget(sourceDict, sourceTag, targetTag)

        for c in couples:
            ID, SOURCE, TARGET = c
            print(ID + "\n" + SOURCE + "\n" + TARGET + "\n")

        return couples
