class SkeletonSerializer(object):
    @staticmethod
    def serialize_function(function_dict, nparams=None):
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
    def serialize_functions(function_dicts, nparams=None):
        ret = []

        if nparams:
            for func, params in zip(function_dicts, nparams):
                ret.append(SkeletonSerializer.serialize_function(func, params))
        else:
            for func in function_dicts:
                ret.append(SkeletonSerializer.serialize_function(func))

        return ret