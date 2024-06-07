"""
Create a dataset of (src, cfg) of the entire CodeSearchNet dataset.
It outputs 3 files corresponding to the 3 splits.
"""
from datasets import load_dataset, Dataset
import ast

# Package must be in the current working dir.
from funcskeleton import SkeletonEncoder, SkeletonSerializer
from funcskeleton.utils import n_params

def sanity_check(_:dict):
    function = _['func_code_string']
    A = SkeletonEncoder.function_sanity_check(function)
    B = '*' not in function # no *args or **kwargs
    return A and B 

if __name__ == '__main__':

    code_search_net = load_dataset(
        'code_search_net', 'python',
        trust_remote_code=True,
    )

    print(f'Before(train): {code_search_net["train"].num_rows}')
    print(f'Before(test):  {code_search_net["test"].num_rows}')
    print(f'Before(validation): {code_search_net["validation"].num_rows}')

    code_search_net['train'] = code_search_net['train'].filter(lambda _: sanity_check(_))
    code_search_net['test'] = code_search_net['test'].filter(lambda _: sanity_check(_))
    code_search_net['validation'] = code_search_net['validation'].filter(lambda _: sanity_check(_))

    print(f'After filtering (train): {code_search_net["train"].num_rows}')
    print(f'After filtering (test): {code_search_net["test"].num_rows}')
    print(f'After filtering (validation): {code_search_net["validation"].num_rows}')

    csn_train = code_search_net['train']
    csn_test  = code_search_net['test']
    csn_val   = code_search_net['validation']
    
    dataset = {'train': [], 'test': [], 'validation': []}

    ### TEST

    print('Loading test functions...', flush=True)
    functions_test = [_['func_code_string'] for _ in csn_test]

    src_cfgs_test = SkeletonEncoder.from_single_functions_parallel(
        functions=functions_test, verbose=True, n_processes=6,
    )

    for src, cfg in src_cfgs_test:
        tree    = ast.parse(src)
        nparams = n_params(tree)
        cfg_str = SkeletonSerializer.serialize_function(cfg, nparams)
        dataset['test'].append({'src':src, 'cfg':cfg_str})

    ### VALIDATION

    print('Loading validation functions...', flush=True)
    functions_val = [_['func_code_string'] for _ in csn_val]

    src_cfgs_val = SkeletonEncoder.from_single_functions_parallel(
        functions=functions_val, verbose=True, n_processes=6,
    )

    for src, cfg in src_cfgs_val:
        tree    = ast.parse(src)
        nparams = n_params(tree)
        cfg_str = SkeletonSerializer.serialize_function(cfg, nparams)
        dataset['validation'].append({'src':src, 'cfg':cfg_str})

    ### TRAIN

    print('Loading train functions...', flush=True)
    functions_train = [_['func_code_string'] for _ in csn_train]

    src_cfgs_train = SkeletonEncoder.from_single_functions_parallel(
        functions=functions_train, verbose=True, n_processes=20,
    )

    for src, cfg in src_cfgs_train:
        tree    = ast.parse(src)
        nparams = n_params(tree)
        cfg_str = SkeletonSerializer.serialize_function(cfg, nparams)
        dataset['train'].append({'src':src, 'cfg':cfg_str})

    ### WRITE DATASET

    hface_validation = Dataset.from_list(dataset['validation'])
    hface_test       = Dataset.from_list(dataset['test'])
    hface_train      = Dataset.from_list(dataset['train'])

    hface_test.to_json('test.json')
    hface_train.to_json('train.json')
    hface_validation.to_json('validation.json')