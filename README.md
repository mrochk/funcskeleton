# FuncSkeleton
Generate the "skeleton" of a function for Machine Learning purposes.

To install this package, first clone this repository, then:
```
cd  funcskeleton
pip install -r requirements.txt
pip install .
```

For a given python (file | piece of source code) it will generate a dictionary in the form: 
```
functions: [
    {
        function1_identifier: ...,
        function1_containing_class: ...,
        function1_blocks: [
            {
                block1_identifier: ...
                block1_control_flow: ...
                block1_relations: ...
                block1_number_of_calls: ...
            }, ...
            
        ]
    }, ...
]

```
Where the *blocks*, similarly as in a Control Flow Graph, give informations regarding each function flow of execution.

This dictionary representation is what we call the list of *skeletons* of each function in the file.

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
    functions=[src1, src2]
) 

serialized = SkeletonSerializer.serialize_functions(control_flow_dicts)

for s in serialized: print(s)
```
