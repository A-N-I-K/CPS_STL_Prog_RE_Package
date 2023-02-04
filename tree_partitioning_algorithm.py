'''
Created on Jan 30, 2023

@author: ANIK
'''

import random

from AlgebraicExpressionParser import ExpressionParser
from AlgebraicExpressionParser import Operator
from AlgebraicExpressionParser import Operators
from treelib import Tree

binaryOperators = ['A', 'O', 'U', 'R']
unaryOperators = ['G', 'F', '!']

qMat = []
qMat.append([-1])


def addNodeRec(selfID, parentID, selfVar, parentVar, synTree, expTree, qMat, qParent):

    if selfID[0] == 0:

        if expTree[selfID[0]][0] == 'G':

            synTree.create_node('(ID: {}) FORALL i_{} \in {}'.format(selfID[0], selfVar[0], expTree[selfID[0]][1:]), selfID[0])

            parentVar = selfVar[0]
            selfVar[0] += 1

            qMat[0].append(0)
            qParent = 0
            qMat.append([0])

        elif expTree[selfID[0]][0] == 'F':

            synTree.create_node('(ID: {}) EXISTS i_{} \in {}'.format(selfID[0], selfVar[0], expTree[selfID[0]][1:]), selfID[0])

            parentVar = selfVar[0]
            selfVar[0] += 1

            qMat[0].append(0)
            qParent = 0
            qMat.append([0])

        elif not (expTree[selfID[0]][0] in binaryOperators or expTree[selfID[0]][0] in unaryOperators):

            synTree.create_node('(\sigma, 0) \models {}'.format(expTree[selfID[0]]), selfID[0])

        else:

            synTree.create_node(expTree[selfID[0]], selfID[0])

    else:

        if parentVar == -1:

            if expTree[selfID[0]][0] == 'G':

                synTree.create_node('(ID: {}) FORALL i_{} \in {}'.format(selfID[0], selfVar[0], expTree[selfID[0]][1:]), selfID[0], parent = parentID)

                parentVar = selfVar[0]
                selfVar[0] += 1

                qMat[0].append(selfID[0])
                qParent = selfID[0]
                qMat.append([qParent])

            elif expTree[selfID[0]][0] == 'F':

                synTree.create_node('(ID: {}) EXISTS i_{} \in {}'.format(selfID[0], selfVar[0], expTree[selfID[0]][1:]), selfID[0], parent = parentID)

                parentVar = selfVar[0]
                selfVar[0] += 1

                qMat[0].append(selfID[0])
                qParent = selfID[0]
                qMat.append([qParent])

            elif not (expTree[selfID[0]][0] in binaryOperators or expTree[selfID[0]][0] in unaryOperators):

                synTree.create_node('(\sigma, 0) \models {}'.format(expTree[selfID[0]]), selfID[0])

            else:

                synTree.create_node(expTree[selfID[0]], selfID[0], parent = parentID)

        else:

            if expTree[selfID[0]][0] == 'G':

                # synTree.create_node('FORALL i_{} \in {} + i_{}{} + i_{}{}'.format(selfVar[0], expTree[selfID[0]][1:expTree[selfID[0]].find(',')], parentVar, expTree[selfID[0]][expTree[selfID[0]].find(','):-1], parentVar, expTree[selfID[0]][-1]), selfID[0], parent = parentID)
                synTree.create_node('(ID: {}) FORALL i_{} \in {} + i_{}{} + i_{}{}'.format(selfID[0], selfVar[0], expTree[selfID[0]][1:expTree[selfID[0]].find(',')], parentVar, expTree[selfID[0]][expTree[selfID[0]].find(','):-1], parentVar, expTree[selfID[0]][-1]), selfID[0], parent = parentID)

                parentVar = selfVar[0]
                selfVar[0] += 1

                for i in range(len(qMat)):

                    if qMat[i][0] == qParent:

                        qMat[i].append(selfID[0])
                        qParent = selfID[0]
                        qMat.append([qParent])

            elif expTree[selfID[0]][0] == 'F':

                synTree.create_node('(ID: {}) EXISTS i_{} \in {} + i_{}{} + i_{}{}'.format(selfID[0], selfVar[0], expTree[selfID[0]][1:expTree[selfID[0]].find(',')], parentVar, expTree[selfID[0]][expTree[selfID[0]].find(','):-1], parentVar, expTree[selfID[0]][-1]), selfID[0], parent = parentID)

                parentVar = selfVar[0]
                selfVar[0] += 1

                for i in range(len(qMat)):

                    if qMat[i][0] == qParent:

                        qMat[i].append(selfID[0])
                        qParent = selfID[0]
                        qMat.append([qParent])

            elif not (expTree[selfID[0]][0] in binaryOperators or expTree[selfID[0]][0] in unaryOperators):

                synTree.create_node('(\sigma, i_{}) \models {}'.format(parentVar, expTree[selfID[0]]), selfID[0], parent = parentID)

            else:

                synTree.create_node(expTree[selfID[0]], selfID[0], parent = parentID)

    if expTree[selfID[0]][0] in binaryOperators:

        parentID = selfID[0]

        selfID[0] += 1
        addNodeRec(selfID, parentID, selfVar, parentVar, synTree, expTree, qMat, qParent)

        selfID[0] += 1
        addNodeRec(selfID, parentID, selfVar, parentVar, synTree, expTree, qMat, qParent)

    if expTree[selfID[0]][0] in unaryOperators:

        parentID = selfID[0]

        selfID[0] += 1
        addNodeRec(selfID, parentID, selfVar, parentVar, synTree, expTree, qMat, qParent)


def genSynTree(exp):

    operators = [Operator(symbol = 'AND', precedence = 2),
                Operator(symbol = 'OR', precedence = 2),
                Operator(symbol = 'G[a, b]', type = Operator.unary, precedence = 3, associativity = Operator.rtl, position = Operator.prefix),
                Operator(symbol = 'F[a, b]', type = Operator.unary, precedence = 3, associativity = Operator.rtl, position = Operator.prefix),
                Operator(symbol = 'U[a, b]', precedence = 2),
                Operator(symbol = 'R[a, b]', precedence = 2),
                Operator(symbol = '!', type = Operator.unary, precedence = 3, associativity = Operator.rtl, position = Operator.prefix)]

    for i in range(len(exp)):

        if exp[i] == '[':

            temporalOperator = exp[i - 1:exp[i:].find(']') + 1 + i]
            operators.append(Operator(symbol = temporalOperator, type = Operator.unary, precedence = 3, associativity = Operator.rtl, position = Operator.prefix))

    operators = Operators(operators)
    parser = ExpressionParser(operators)
    expTree = parser.syntax_tree(exp).preorder()

    synTree = Tree()
    selfID = [0]
    selfVar = [0]

    # qMat = []
    # qMat.append([-1])

    addNodeRec(selfID, 0, selfVar, -1, synTree, expTree, qMat, -1)

    printMatrix(qMat)

    return synTree


def getNodeData(synTree, nodeID):

    return synTree[nodeID].tag


def getNodeInterval(synTree, nodeID):

    tag = synTree.get_node(nodeID).tag
    start = (tag[tag.find('[') + 1: tag.find(',')])
    end = (tag[tag.find(',') + 2: tag.find(']')])

    return start, end


def getSubTree(synTree, nodeID):

    subTree = Tree()

    currentID = '{}'.format(subTree.create_node(synTree.get_node(nodeID).tag, random.randrange(100, 1000000)))
    currentID = int(currentID[currentID.find('identifier=') + 11:currentID.find(', data=')])

    def copyNodeRec(synTree, nodeID, parentID):

        if not synTree.get_node(nodeID).is_leaf():

            childrenList = synTree.children(nodeID)

            for child in childrenList:

                currentID = '{}'.format(child)
                currentID = '{}'.format(subTree.create_node(currentID[currentID.find('tag=') + 4:currentID.find(', identifier=')], random.randrange(100, 1000000), parent = parentID))
                currentID = int(currentID[currentID.find('identifier=') + 11:currentID.find(', data=')])

                nodeID = '{}'.format(child)
                nodeID = int(nodeID[nodeID.find('identifier=') + 11:nodeID.find(', data=')])

                # print(synTree.all_nodes())
                # print(nodeID, currentID)

                copyNodeRec(synTree, nodeID, currentID)

    copyNodeRec(synTree, nodeID, currentID)

    # print(subTree.all_nodes())

    return subTree


def treePartition(synTree, qMat, nodeID, time):

    if nodeID == -1 and qMat[0][1] == 0:

        newRoot = Tree()
        tag = synTree.get_node(0).tag

        if 'FORALL' in tag:

            rootID = newRoot.create_node('AND', random.randrange(100, 1000000)).identifier

        if 'EXISTS' in tag:

            rootID = newRoot.create_node('OR', random.randrange(100, 1000000)).identifier

        # subTreeOne = getSubTree(synTree, 0)
        subTreeTwo = getSubTree(synTree, 0)

        # newRoot.paste(rootID, subTreeOne)
        newRoot.paste(rootID, subTreeTwo)

        synTree.get_node(0).tag = '{}{})'.format(tag[:tag.find(',') + 2], time)
        subTreeTwo.get_node(subTreeTwo.root).tag = '{}{}{}'.format(tag[:tag.find('[') + 1], time, tag[tag.find(','):])

        for i in range(len(qMat[1]) - 1):

            partNode(synTree, qMat[1][i + 1], time)
            treePartition(synTree, qMat, qMat[1][i + 1], time)

        subTreeOne = getSubTree(synTree, 0)
        newRoot.paste(rootID, subTreeOne)

        synTree = newRoot
        return synTree

    else:

        for j in range(len(qMat)):

            if qMat[j][0] == nodeID and len(qMat[j]) > 1:

                print(j, len(qMat[j]))

                for i in range(len(qMat[j]) - 1):

                    # print(qMat[j][i + 1])

                    partNode(synTree, qMat[j][i + 1], time)
                    treePartition(synTree, qMat, qMat[j][i + 1], time)


def partNode(synTree, nodeID, time):
    
    parentID = synTree.parent(nodeID).identifier
    tag = synTree.get_node(nodeID).tag

    # parentNode = synTree.parent(nodeID)
    
    if 'FORALL' in tag:

        newParentID = synTree.create_node('AND', random.randrange(100, 1000000), parent = parentID).identifier
        synTree.move_node(nodeID, newParentID)

        subTree = getSubTree(synTree, nodeID)
        subTree.get_node(subTree.root).tag = '{}{}{}'.format(tag[:tag.find('[') + 1], time, tag[tag.find(','):])

        synTree.paste(newParentID, subTree)
        
        synTree.get_node(nodeID).tag = '{}{})'.format(tag[:tag.find(',') + 2], time)

        # synTree.get_node(nodeID).tag = '{}'

        # synTree.show()

    if 'EXISTS' in tag:

        newParentID = synTree.create_node('OR', random.randrange(100, 1000000), parent = parentID).identifier
        synTree.move_node(nodeID, newParentID)

        subTree = getSubTree(synTree, nodeID)
        subTree.get_node(subTree.root).tag = '{}{}{}'.format(tag[:tag.find('[') + 1], time, tag[tag.find(','):])

        synTree.paste(newParentID, subTree)

        synTree.get_node(nodeID).tag = '{}{})'.format(tag[:tag.find(',') + 2], time)

        # synTree.get_node(nodeID).tag = '{}'

        # synTree.show()


def printMatrix(qMat):

    testPrint = "";

    # qMat = [[1, 2], [3, 4]]

    for i in range(len(qMat)):

        for j in range(len(qMat[i])):

            testPrint += "{} ".format(qMat[i][j])

        print(testPrint)
        testPrint = ""

    print()


def main():

    # tr = parser.syntax_tree('(a + b) * c').preorder()
    # exp = '(a + b) * sin(sin(c))'
    # exp = '(a + b) * (c + d)'
    # exp = 'G[a, b](F[a, b] A)'
    # exp = 'F[a, b](F[a, b](G[a, b]p) AND G[a, b] !(q OR G[a, b]r))'
    exp = 'F[0, 10](p AND G[0, 5] !q)'
    # exp = 'F[0, 10]p'
    
    # tr = parser.postfix(exp)
    # tr = parser.syntax_tree(exp).preorder()
    #
    # print(parser.postfix(exp))
    # print(parser.syntax_tree(exp).preorder())
    # print(parser.syntax_tree(exp).inorder())
    # print(parser.syntax_tree(exp).postorder())

    synTree = genSynTree(exp)
    # synTree.show()

    # print(getNodeInterval(synTree, 3))

    # partNode(synTree, 3, 5)

    synTree = treePartition(synTree, qMat, -1, 5)
    synTree.show()

    # print(getNodeData(synTree, 0))

    return

if __name__ == '__main__':

    main()
    pass
