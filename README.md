# FuncSkeleton
Generates the "skeleton" of a function for Machine Learning purposes.

That is, for a given python (file | piece of source code) it will generate a dictionary in the form: 
```
functions: [
    {
        function1_identifier: ...,
        function1_containing_class: ...,
        function1_blocks: [
            {
                function1_block1_identifier: ...
                function1_block1_control_flow: ...
                function1_block1_relations: ...
                function1_block1_number_of_calls: ...
            }, ...
            
        ]
    }, ...
]

```
Where the *blocks*, similarly as in a Control Flow Graph, give informations regarding each function flow of execution.

This dictionary representation is what I call the list of *skeletons* of each function in the file.

***This program does not support functions containing nested classes or functions.***\
***It will simply skip them.***

## *Example:*
```python
from funcskeleton import SkeletonEncoder, SkeletonSerializer

src1 = """
def function1(param):
    print(param)

    for i in range(100): 
        function2(i)
        function2(i+1)
    
    if param:
        if function2(param) : return 1
    else: return 2
"""

src2 = """
def function2(param):
    for i in range(100): 
        return function1(i) + function2(i)
    
    if param: function1(param)
    else: function2(param)

    return param
"""

control_flow_dicts = SkeletonEncoder.from_single_functions(
    functions=[src1, src2], 
) 

serialized = SkeletonSerializer.serialize_functions(control_flow_dicts)

for s in serialized: print(s)

# [None][For][None][If][If][Return][Return];[1][2,3][1][4,5][6][][];[1][1][2][0][1][0][0]
# [For][Return][If][None][None][Return];[1,2][][3,4][5][5][];[1][2][0][1][1][0]
```
