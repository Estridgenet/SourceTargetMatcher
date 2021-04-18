# Sample SDLXLIFF tagging:
# <target><mrk mtype="seg" mid="5"/></target>
# <seg-source><mrk mtype="seg" mid="5">Drawing_references_to_be_translated:</mrk>

# Sample XLIFF tagging:


# TODO: Cleanup, can probably just use one dfs structure


'''
<body>
<trans-unit id="0000000001" datatype="x-text/xml" restype="string">
<source>人机交互系统及其方法、终端设备</source>
<target/>
</trans-unit>
</body>
'''

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