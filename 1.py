from random import randint

envelop_x, envelop_y = x,y =randint(0,100), randint(0,100)
paper_x, paper_y = a,b = randint(0,100), randint(0,100)

def check(x,y,a,b):
    return (a < x and b < y) or (b < x and a < y)

print(f'''Конверт: длина - {x}, ширина - {y}
Лист:    длина - {a}, ширина - {b}
Вместится? ответ - {check(x,y,a,b)}''')



