# FuncSkeleton
Generate the CFG "skeleton" of a function for Machine Learning purposes.

This tool is based on [`scalpel`](https://github.com/SMAT-Lab/Scalpel).

To install this package, first clone this repository, then:
```bash
cd  funcskeleton
pip install -r requirements.txt
pip install .
```

For a given python input, it will generate a dictionary in the form: 
```
functions: [
    {
        function1_name: ...,
        function1_parent_class: ...,
        function1_blocks: [
            {
                block1_id: ...
                block1_ctrl_flow: ...
                block1_relations: ...
                block1_n_calls: ...
            }, ...
            
        ]
    }, ...
]

```
Where the *blocks*, as in the Control Flow Graph, give informations regarding each function flow of execution.

This dictionary representation is what we call the list of *skeletons* of each function in the file.

This program does not support functions containing nested classes or functions.\
It will simply skip them.

## *Example:*
```python
src = """
def function1(param):
    print(param)

    for i in range(100): 
        function2(i)
        function2(i+1)
    
    if param:
        if function2(param) : return 1
    else: return 2
"""

from funcskeleton import SkeletonEncoder, SkeletonSerializer

_, enc = SkeletonEncoder.from_single_functions(functions=[src])[0]

result = SkeletonSerializer.serialize_function(enc)

print(result)

# [None][For][None][If][If][Return][Return];[1][2,3][1][4,5][6][][];[1][1][2][0][1][0][0]
```

Note: In https://huggingface.co/datasets/mrochk/src_ast_cfg, we use `SkeletonSerializer.serialize_function_separators_numbered`.
