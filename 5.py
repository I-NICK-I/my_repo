from random import choice


some_set = [
    [1,[]],
    ['ab',1],
    ['ab',0.5],
    ['ab',''],
    [1,0.5],
    [1,2],
    [1,False],
    [1,'2']
            ]
some_list = choice(some_set)

def is_all_int(lst):
    print(lst)
    return all(True if type(x) is int else False for x in lst)
    
print(is_all_int(some_list))