import ast
from collections import deque

def get_ast_nodes_dfs(tree:ast.AST):
    def dfs(node, queue=deque()):
        queue.append(type(node).__name__.upper())
        for child in ast.iter_child_nodes(node):
            queue = dfs(child, queue)
        return queue

    return ' '.join(dfs(tree))