'''
Created on Jan 30, 2023

@author: ANIK
'''

import ast

from AlgebraicExpressionParser import ExpressionParser
from AlgebraicExpressionParser import Operator
from AlgebraicExpressionParser import Operators

from treelib import Node, Tree

# binaryOperators = ['+', '-', '*', '^']
# unaryOperators = ['sin']

binaryOperators = ['AND', 'OR', 'U[a, b]', 'R[a, b]']
unaryOperators = ['G[a, b]', 'F[a, b]', '!']

# def addNodeRec(selfID, parentID, synTree, expTree):
#
#     if selfID[0] == 0:
#
#         synTree.create_node(expTree[selfID[0]], selfID[0])
#
#     else:
#
#         synTree.create_node(expTree[selfID[0]], selfID[0], parent = parentID)
#
#     if expTree[selfID[0]] in binaryOperators:
#
#         parentID = selfID[0]
#
#         selfID[0] += 1
#         addNodeRec(selfID, parentID, synTree, expTree)
#
#         selfID[0] += 1
#         addNodeRec(selfID, parentID, synTree, expTree)
#
#     if expTree[selfID[0]] in unaryOperators:
#
#         parentID = selfID[0]
#
#         selfID[0] += 1
#         addNodeRec(selfID, parentID, synTree, expTree)


def addNodeRec(selfID, parentID, selfVar, parentVar, synTree, expTree):

    if selfID[0] == 0:

        if expTree[selfID[0]][0] == 'G':

            synTree.create_node('FORALL i_{} \in {}'.format(selfVar[0], expTree[selfID[0]][1:]), selfID[0])

            parentVar = selfVar[0]
            selfVar[0] += 1

        elif expTree[selfID[0]][0] == 'F':

            synTree.create_node('EXISTS i_{} \in {}'.format(selfVar[0], expTree[selfID[0]][1:]), selfID[0])

            parentVar = selfVar[0]
            selfVar[0] += 1

        else:

            synTree.create_node(expTree[selfID[0]], selfID[0])

    else:

        if parentVar == -1:

            if expTree[selfID[0]][0] == 'G':

                synTree.create_node('FORALL i_{} \in {}'.format(selfVar[0], expTree[selfID[0]][1:]), selfID[0], parent = parentID)

                parentVar = selfVar[0]
                selfVar[0] += 1

            elif expTree[selfID[0]][0] == 'F':

                synTree.create_node('EXISTS i_{} \in {}'.format(selfVar[0], expTree[selfID[0]][1:]), selfID[0], parent = parentID)

                parentVar = selfVar[0]
                selfVar[0] += 1

            else:

                synTree.create_node(expTree[selfID[0]], selfID[0], parent = parentID)

        else:

            if expTree[selfID[0]][0] == 'G':

                synTree.create_node('FORALL i_{} \in {} + i_{}{} + i_{}{}'.format(selfVar[0], expTree[selfID[0]][1:expTree[selfID[0]].find(',')], parentVar, expTree[selfID[0]][expTree[selfID[0]].find(','):-1], parentVar, expTree[selfID[0]][-1]), selfID[0], parent = parentID)

                parentVar = selfVar[0]
                selfVar[0] += 1

            elif expTree[selfID[0]][0] == 'F':

                synTree.create_node('EXISTS i_{} \in {} + i_{}{} + i_{}{}'.format(selfVar[0], expTree[selfID[0]][1:expTree[selfID[0]].find(',')], parentVar, expTree[selfID[0]][expTree[selfID[0]].find(','):-1], parentVar, expTree[selfID[0]][-1]), selfID[0], parent = parentID)

                parentVar = selfVar[0]
                selfVar[0] += 1

            else:

                synTree.create_node(expTree[selfID[0]], selfID[0], parent = parentID)

    if expTree[selfID[0]] in binaryOperators:

        parentID = selfID[0]

        selfID[0] += 1
        addNodeRec(selfID, parentID, selfVar, parentVar, synTree, expTree)

        selfID[0] += 1
        addNodeRec(selfID, parentID, selfVar, parentVar, synTree, expTree)

    if expTree[selfID[0]] in unaryOperators:

        parentID = selfID[0]

        selfID[0] += 1
        addNodeRec(selfID, parentID, selfVar, parentVar, synTree, expTree)


def genSynTree(exp):

    # operators = [Operator(symbol = '+'),
    #              Operator(symbol = '-'),
    #              Operator(symbol = '*', precedence = 2),
    #              Operator(symbol = '-', type = Operator.unary, precedence = 3, associativity = Operator.rtl, position = Operator.prefix),
    #              Operator(symbol = '^', precedence = 4),
    #              Operator(symbol = 'sin', type = Operator.unary, precedence = 3, associativity = Operator.rtl, position = Operator.prefix)]

    operators = [Operator(symbol = 'AND', precedence = 2),
                Operator(symbol = 'OR', precedence = 2),
                Operator(symbol = 'G[a, b]', type = Operator.unary, precedence = 3, associativity = Operator.rtl, position = Operator.prefix),
                Operator(symbol = 'F[a, b]', type = Operator.unary, precedence = 3, associativity = Operator.rtl, position = Operator.prefix),
                Operator(symbol = 'U[a, b]', precedence = 2),
                Operator(symbol = 'R[a, b]', precedence = 2),
                Operator(symbol = '!', type = Operator.unary, precedence = 3, associativity = Operator.rtl, position = Operator.prefix)]

    operators = Operators(operators)
    parser = ExpressionParser(operators)
    expTree = parser.syntax_tree(exp).preorder()

    synTree = Tree()
    selfID = [0]
    selfVar = [0]

    addNodeRec(selfID, 0, selfVar, -1, synTree, expTree)

    return synTree


def convertToParseTree(synTree):

    return


def getNodeData(synTree, nodeID):

    return synTree[nodeID].tag


def main():

    # tr = parser.syntax_tree('(a + b) * c').preorder()
    # exp = '(a + b) * sin(sin(c))'
    # exp = '(a + b) * (c + d)'
    # exp = 'G[a, b](F[a, b] A)'
    exp = 'F[a, b](F[a, b](G[a, b]p) AND G[a, b] !(q OR G[a, b]r))'
    
    # tr = parser.postfix(exp)
    # tr = parser.syntax_tree(exp).preorder()
    #
    # print(parser.postfix(exp))
    # print(parser.syntax_tree(exp).preorder())
    # print(parser.syntax_tree(exp).inorder())
    # print(parser.syntax_tree(exp).postorder())

    synTree = genSynTree(exp)
    synTree.show()

    print(getNodeData(synTree, 0))

    return

if __name__ == '__main__':

    main()
    pass
