from random import randint


amount_of_cubs = randint(1,10)

def count_of_sixes(integer):
    sides = 6
    answer = 0
    if integer == 1:
        dikt = {1: randint(1, sides)}
    else:
        dikt = {x: randint(1, sides) for x in range(1,integer+1)}
    [print(x) for x in dikt.items()]
    for k,v in dikt.items():
        if v == 6:
            answer += 1
        else:
            continue
    return answer
    
print(f'Количество кубиков с выпавшей "шестёркой": {count_of_sixes(amount_of_cubs)}')