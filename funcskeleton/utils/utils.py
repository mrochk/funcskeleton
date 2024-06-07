from sys import stderr
from termcolor import colored
import ast

def log_error(message):
    """
    Log an error to stderr in red.
    """
    message = colored(message, 'red')
    print(message, file=stderr, flush=True)

def n_params(node:ast.AST):
    """
    Returns the number of params for an AST containing
    a *single* function.
    """
    for child in ast.walk(node):
        if isinstance(child, ast.FunctionDef):
            return len(child.args.args)
    return 0