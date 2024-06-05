import ast

class Block(object):

    def __init__(self, scalpel_block, in_main):
        self.scalpel = scalpel_block
        self.identifier = self.scalpel.id
        self.relations = [_.target.id for _ in self.scalpel.exits]
        self.control_flow = None
        self.calls = []

        self.calls_ast = set()
        ctrlflow_count = 0
        # idk if it is useful or not to iterate through all 
        # the statements and not only the first
        for stmt in self.scalpel.statements:
            self.calls_ast = self.calls_ast.union(
                self.__get_calls_main(stmt) if in_main else self.__get_calls(stmt)
            )

            if self.__isctrlflow(stmt):
                self.control_flow = type(stmt).__name__
                ctrlflow_count += 1

        # my assumption is that there is only one possible ctrl flow 
        # statement (if, for, while...) per cfg block
        assert ctrlflow_count <= 1

    def __get_calls(self, stmt : ast.AST, calls=[]):
        calls = calls.copy()

        for child in ast.iter_child_nodes(stmt):
            if isinstance(child, ast.Call): 
                calls.append(child.func)
            calls = self.__get_calls(child, calls)

        return calls

    def __get_calls_main(self, stmt : ast.AST, calls=[]):
        calls = calls.copy()

        # if it is a block in main, we stop when encoutering
        # either a class of function definition, else it will
        # include it in the list of calls
        if isinstance(stmt, (ast.FunctionDef, ast.ClassDef)):
            return calls

        for child in ast.iter_child_nodes(stmt):
            if isinstance(child, ast.Call): 
                calls.append(child.func)
            calls = self.__get_calls(child, calls)

        return calls

    @staticmethod
    def __isctrlflow(stmt : ast.AST):
        t = (ast.If, ast.For, ast.While, ast.Return)
        return isinstance(stmt, t)
        
    def calls_to_identifiers(self):
        iscall = lambda e: isinstance(e, (ast.Attribute, ast.Name))
        isattr = lambda e: isinstance(e, ast.Attribute)

        for call in self.calls_ast:
            if not iscall(call): continue

            if isattr(call):
                self.calls.append(call.attr)
                continue

            self.calls.append(call.id)

    def to_dict(self):
        return {
            'identifier': self.identifier,
            'control_flow': self.control_flow,
            'relations': self.relations,
            'n_calls': len(self.calls),
        }