import ast
import scalpel.cfg as cfg

from.function import Function

class Graph(object):

    def __init__(self, src):

        try: ast.parse(src)
        except SyntaxError: raise SyntaxError

        self.functions = []

        classes = self.__classes(src)

        try: scalpel_cfg = cfg.CFGBuilder().build_from_src(
                name='cfg',
                src=src,
                flattened=True, # returns a dict of graphs: one per function
            )
        except Exception: raise ScalpelError

        class_prefix = None

        for name, scalpel_element in scalpel_cfg.items():
            name = self.__parse_scalpel_name(name)

            if not self.__mainfunction(name):

                if name in classes:
                    class_prefix = name
                    continue

                function = Function(scalpel_element, class_prefix)
                self.functions.append(function)

    @staticmethod
    def from_file(filepath):
        with open(filepath) as f:
            src = f.read()

        return Graph(src)
    
    @staticmethod
    def __classes(src):
        """
        Get all the classes in Python source code.
        """
        tree = ast.parse(src)

        def aux(root : ast.AST, classes=set()):
            if isinstance(root, ast.ClassDef):
                classes.add(root.name)

            for child in ast.iter_child_nodes(root):
                classes = aux(child, classes)

            return classes
        
        return aux(tree)

    @staticmethod
    def __parse_scalpel_name(name):
        return name.replace('mod.', '')

    @staticmethod
    def __mainfunction(name):
        return name == 'mod'

    def to_dict(self):
        return {
            'functions': [f.to_dict() for f in self.functions]
        }

class ScalpelError(Exception):
    "Error coming from Scalpel when building the CFG."
    pass