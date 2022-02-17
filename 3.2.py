from datetime import datetime
from random import randint

def first():
    start = datetime.now()
    [[i for i in range(20)] for _ in range(20)]
    end = datetime.now()
    return((end - start).microseconds)

def second():
    start = datetime.now()
    [(i for i in range(20)) for _ in range(20)]
    end = datetime.now()
    return((end - start).microseconds)

def third():
    start = datetime.now()
    ((i for i in range(20)) for _ in range(20))
    end = datetime.now()
    return((end - start).microseconds)

cicles = randint(50,100)
first  = ('first: [[i for i in range(20)] for _ in range(20)]' , sum(first()  for x in range(cicles))/cicles)
second = ('second: [(i for i in range(20)) for _ in range(20)]', sum(second() for x in range(cicles))/cicles)
third  = ('third: ((i for i in range(20)) for _ in range(20))' , sum(third()  for x in range(cicles))/cicles)

result = sorted([first, second, third], key = lambda x : x[1])
[print(x) for x in result]
 
print(f'''number of cicles: {cicles}
fastest of all - {result[0][0]} time: {result[0][1]}
all results:''')
[print(x) for x in result]





