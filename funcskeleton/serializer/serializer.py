from abc import ABC

class SkeletonSerializer(ABC):
    """
    Abstract class containing methods for serializing a dictionary
    produced by SkeletonEncoder (that is, converting it to text).
    """
    @staticmethod
    def serialize_function(function_dict:dict, nparams:int=None) -> str:
        """
        Takes a function dictionary produced by SkeletonEncoder, and returns a 
        string in the form: `[n_params_func (if specified)];[ctrl_flow_block1]
        ...[ctrl_flow_blockN];[relations_block1]...[relations_blockN];
        [n_calls_block1]...[n_class_blockN]`.
        """
        ret, blocks = '', function_dict['blocks']

        if nparams:
            ret += f'[{nparams}];'

        for block in blocks:
            ctrlflow = block['control_flow']
            ret += f'[{ctrlflow}]'
        ret += ';'

        for block in blocks:
            relations = block['relations']
            ret += str(relations).replace(' ', '')
        ret += ';'

        for block in blocks:
            calls = block['n_calls']
            ret += f'[{calls}]'

        return ret

    @staticmethod
    def serialize_functions(function_dicts:list[dict], nparams:list[int]=None) -> list[str]:
        """
        Calls `serialize_function` on a list of function dicts, for `nparams`,
        it must be a list of integers s.t `nparams[i] == n_params(func_i)`.
        """
        ret = []

        if nparams:
            for func, params in zip(function_dicts, nparams):
                ret.append(SkeletonSerializer.serialize_function(func, params))
        else:
            for func in function_dicts:
                ret.append(SkeletonSerializer.serialize_function(func))

        return ret