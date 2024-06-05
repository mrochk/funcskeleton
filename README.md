# FuncSkeleton
Generates the "skeleton" of a function for Machine Learning purposes.

Example:
```python
import funcskeleton as fs

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

control_flow_dicts = fs.Encoder.dicts_from_single_functions(
    functions=[src1, src2], 
) 

serialized = fs.Serializer.serialize_functions(control_flow_dicts)

for s in serialized: print(s)

# [None][For][None][If][If][Return][Return];[1][2,3][1][4,5][6][][];[1][1][2][0][1][0][0]
# [For][Return][If][None][None][Return];[1,2][][3,4][5][5][];[1][2][0][1][1][0]
```