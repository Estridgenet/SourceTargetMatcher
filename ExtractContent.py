import re

# Sample XLIFF tagging:
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
    Search the tree dict for content.

    See XLIFFParser2 for information about the node class and
    the representation of the data tree.

    Args:
        dataTree: list of nodes from the XLIFFParser2.
    """

    def __init__(self, dataTree):
        self.dataTree = self.getTreeDict(dataTree)
        self.matchDict = dict()

    def getTreeDict(self, treeList):
        """Convert node list into dictionary with root node tag as key.

        The node list is converted into a dictionary with the tags of the root
        nodes as dictionary keys and the corresponding root nodes as values.

        Returns:
            dictionary with corresponding nodes in a list of dictionary values.
        """

        tagDict = defaultdict(list)

        for node in treeList:
            tagDict[node.tag].append(node)

        return tagDict

    def dfsSource(self, sourceTag):
        """Search for content of all trees with given source param as root node.

        If tag paths are not unique in tree, they will be overwritten.

        Args:
            sourceTag (string): xml tag to be searched for, e.g. 'source'

        Returns:
            dictionary with full root-to-node pathname as key and content
            associated with end node as dictionary value."""

        dfsDict = dict()
        for sourceNode in self.dataTree[
            sourceTag
        ]:  # this deletes nodes if said nodes don't have unique tag id & attribute structures
            self.dfsSourceHelper("", sourceNode, dfsDict)

        return dfsDict

    def dfsSourceHelper(self, curPath, curNode, treeDict):
        """Search the tree of a root node for content.

        Args:
            curPath (string): current root-to-node path taken, including attributes.
            Used as key for treeDict.
            curNode (node): current Node being examined.
            treeDict (dict): dict using curPath as key and curNode.content as value.

        Returns:
            treeDict
        """

        curPath += "/" + curNode.tag

        for attrID, attrVal in curNode.attributes.items():

            curPath += "," + attrID + "=" + attrVal

        if curNode.content:
            treeDict[curPath] = self.stringify(curNode.content)

        for subTree in curNode.children:
            self.dfsSourceHelper(curPath, subTree, treeDict)

        return treeDict

    def dfsTarget(self, sourceDict, sourceTag, targetTag):
        """Search for content of all target trees with given param as root node.

        Args:
            sourceDict (dict): dictionary of path - content pairs from dfsSource
            sourceTag (string): source tag that was searched for
            targetTag (string): corresponding target tag to be searched for.


        Returns:
        """

        matches = []
        for targetNode in self.dataTree[targetTag]:
            self.dfsTargetFinder("", sourceTag, targetNode, sourceDict, matches)

        return matches

    def dfsTargetFinder(self, curPath, matchTag, curNode, sourceDict, matches):
        """Search for target path corresponding to source path.

        Args:
            curPath (string): current path in the current node tree.
            matchTag (string): source tag to be matched against.
            curNode (Node): current Node in the tree.
            sourceDict (dict): dictionary of path-content pairs from dfsSource.
            matches (list): list of source-target content matches and source path.
        """

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
        """Turn list of strings into single string."""

        string = ""
        for c in content:
            string += c + "\n"
        return string

    def findIPCCode(self):
        """look for tag with IPC data nodes trees.

        Returns:
            tuple containing generic 4-digit IPC code and specific IPC sub-code in
            the following format: (G02W, 13/00)
            if one or more items is not found, will return (None, None).
        """

        for node in self.dataTree["st"]:
            content = self.stringify(node.content)

            # For Abstracts
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
            # For Reports
            if re.search("classifications-ipcr", content):

                IPCGROUPS = r"[&]gt[;]([\w][\d]+[\w])[\s]+([\d]+[/][\d]+)"

                result = re.search(IPCGROUPS, content)
                # print(result.group(1), result.group(2))
                if result:
                    return result.group(1), result.group(2)

        return None, None

    def findSourceTargetMatch(self, sourceTag, targetTag):
        """Match content of node trees with root source & target tag.

        This method compares full path through node tree (including attributes)
        of source and target.If it finds a full match of tree path with
        only sourceTag and targetTag being swapped, it will pair the content
        of said nodes (if any). For example:

        source/mrk,id=1/text
        target/mrk,id=1/text
        would be a match, and any content corresponding to the two nodes would be paired.

        Args:
            sourceTag (string): source tag to be found.  most likely "seg-source"
            targetTag (string): target tag to be found.  most likely "target"

        Returns:
            list of sub-lists, the sub-lists containing the source path to matched content (string),
            the source content (string), and the target content (string).
        """

        sourceDict = self.dfsSource(sourceTag)
        couples = self.dfsTarget(sourceDict, sourceTag, targetTag)

        for c in couples:
            ID, SOURCE, TARGET = c

        return couples
