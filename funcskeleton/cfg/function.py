from .block import Block

class Function(object):

    def __init__(self, scalpel_func, containing_class=None):

        self.blocks = []
        self.entry = None
        self.containing_class = containing_class
        self.scalpel = scalpel_func
        self.identifier = self.__parse_scalpel_name(scalpel_func.name)
        self.blockmap = dict()

        entry_id = self.scalpel.entryblock.id

        main = self.identifier == '__main__'

        for scalpel_block in self.scalpel.get_all_blocks():
            block = Block(scalpel_block, main)

            if block.identifier == entry_id:
                self.entry = block

            self.blockmap[block.identifier] = block
            self.blocks.append(block)

        assert (self.entry is not None)

        self.__prune_calls(self.entry)
        
        self.__block_calls_to_identifiers()

        self.__change_block_identifiers()

    @staticmethod
    def __parse_scalpel_name(name):
        return '__main__' if name == 'cfg' else name

    def __prune_calls(self, block : Block, callers=set()):
        """
        Delete redundant parent nodes func calls.
        TODO: This function is the bottleneck of this project, 
              it must (no doubt that its possible) be optimized.
        """
        calls_before = block.calls_ast.copy()

        for next_block_id in block.relations:
            next_block = self.blockmap[next_block_id]

            if not (next_block_id in callers): # avoid infinite recursion 
                callers_ = callers.copy()
                callers_.add(block.identifier)
                calls = self.__prune_calls(next_block, callers_)
                block.calls_ast = block.calls_ast.difference(calls)

        return calls_before

    def __block_calls_to_identifiers(self):
        for block in self.blocks:
            block.calls_to_identifiers()

    def __change_block_identifiers(self):
        """
        'Scales' block identifiers to be starting from 0.
        """
        new_identifier = 0
        old2new = {}
        for block in self.blocks:
            old = block.identifier
            old2new[old] = new_identifier
            new_identifier += 1

        for block in self.blocks:
            old = block.identifier
            new = old2new[old]
            block.identifier = new

            for i, old in enumerate(block.relations):
                new = old2new[old]
                block.relations[i] = new

    def to_dict(self):
        return {
            'identifier': self.identifier,
            'containing_class': self.containing_class,
            'blocks': [b.to_dict() for b in self.blocks],
        }

