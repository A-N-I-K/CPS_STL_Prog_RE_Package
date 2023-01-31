'''
Created on Jan 30, 2023

@author: ANIK
'''

import ast

from AlgebraicExpressionParser import ExpressionParser
from AlgebraicExpressionParser import Operator
from AlgebraicExpressionParser import Operators

# from TreeNode import TreeNode, printHeapTree
from treelib import Node, Tree

# binaryOperators = ['+', '-', '*', '^']
# unaryOperators = ['sin']

binaryOperators = ['AND', 'OR', 'U[a, b]', 'R[a, b]']
unaryOperators = ['G[a, b]', 'F[a, b]', '!']

# selfID = [0]

# class Evaluator(ast.NodeTransformer):
#     ops = {
#         ast.Add: '+',
#         ast.Sub: '-',
#         ast.Mult: '*',
#         ast.Div: '/',
#         # define more here
#     }
#
#     def visit_BinOp(self, node):
#         self.generic_visit(node)
#         if isinstance(node.left, ast.Num) and isinstance(node.right, ast.Num):
#             # On Python <= 3.6 you can use ast.literal_eval.
#             # value = ast.literal_eval(node)
#             value = eval(f'{node.left.n} {self.ops[type(node.op)]} {node.right.n}')
#             return ast.Num(n = value)
#         return node


def addNodeRec(selfID, parentID, synTree, expTree):

    if selfID[0] == 0:

        synTree.create_node(expTree[selfID[0]], selfID[0])

    else:

        synTree.create_node(expTree[selfID[0]], selfID[0], parent = parentID)

    if expTree[selfID[0]] in binaryOperators:

        parentID = selfID[0]

        selfID[0] += 1
        addNodeRec(selfID, parentID, synTree, expTree)

        selfID[0] += 1
        addNodeRec(selfID, parentID, synTree, expTree)

    if expTree[selfID[0]] in unaryOperators:

        parentID = selfID[0]

        selfID[0] += 1
        addNodeRec(selfID, parentID, synTree, expTree)


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

    addNodeRec(selfID, 0, synTree, expTree)

    synTree.show()


def main():

    # tr = parser.syntax_tree('(a + b) * c').preorder()
    # exp = '(a + b) * sin(sin(c))'
    # exp = '(a + b) * (c + d)'
    exp = 'A U[a, b] B'
    
    # tr = parser.postfix(exp)
    # tr = parser.syntax_tree(exp).preorder()
    #
    # print(parser.postfix(exp))
    # print(parser.syntax_tree(exp).preorder())
    # print(parser.syntax_tree(exp).inorder())
    # print(parser.syntax_tree(exp).postorder())

    genSynTree(exp)

    return

if __name__ == '__main__':

    main()
    pass
