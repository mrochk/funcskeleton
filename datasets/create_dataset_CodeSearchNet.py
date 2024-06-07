"""
Create a dataset of (src, cfg) of the entire CodeSearchNet dataset.
It outputs 3 files corresponding to the 3 splits.
"""
from datasets import load_dataset, Dataset
import ast

# Requires to have the package in the current working dir.
from funcskeleton import SkeletonEncoder, SkeletonSerializer
from funcskeleton.util import n_params

def sanity_check(_:dict):
    function = _['func_code_string']
    A = SkeletonEncoder.function_sanity_check(function)
    B = '*' not in function # no *args or **kwargs
    return A and B 

if __name__ == '__main__':

    csn = load_dataset(
        'code_search_net', 'python',
        trust_remote_code=True,
    )

    print(f'Before(train): {csn["train"].num_rows}')
    print(f'Before(test):  {csn["test"].num_rows}')
    print(f'Before(validation): {csn["validation"].num_rows}')

    #csn['train'] = csn['train'].filter(lambda _: sanity_check(_))
    csn['test'] = csn['test'].filter(lambda _: sanity_check(_))
    #csn['validation'] = csn['validation'].filter(lambda _: sanity_check(_))

    #print(f'After filtering (train): {csn["train"].num_rows}')
    print(f'After filtering (test): {csn["test"].num_rows}')
    #print(f'After filtering (validation): {csn["validation"].num_rows}')

    csn_train, csn_test, csn_val = csn['train'], csn['test'], csn['validation']
    
    dataset = {'train': [], 'test': [], 'validation': []}

    ### TEST

    print('Loading test functions...', flush=True)
    functions_test = [_['func_code_string'] for _ in csn_test]

    #src_cfgs_test = SkeletonEncoder.from_single_functions_parallel(
        #functions=functions_test, verbose=True, n_processes=6,
    #)

    src_cfgs_test = SkeletonEncoder.from_single_functions(
        functions=functions_test, verbose=True
    )

    for src, cfg in src_cfgs_test:
        tree    = ast.parse(src)
        nparams = n_params(tree)
        cfg_str = SkeletonSerializer.serialize_function(cfg, nparams)
        dataset['test'].append({'src':src, 'cfg':cfg_str})

    ### VALIDATION

    """

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

    """

    ### WRITE DATASET

    hface_test       = Dataset.from_list(dataset['test'])
    #hface_train      = Dataset.from_list(dataset['train'])
    #hface_validation = Dataset.from_list(dataset['validation'])

    hface_test.to_json('test.json')
    #hface_train.to_json('train.json')
    #hface_validation.to_json('validation.json')