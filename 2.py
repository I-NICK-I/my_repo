def plus_one(obj):
    if 'attr' not in obj.__dict__.keys():
        return ('object have no attribute "attr"')
    if type(obj.attr) == int:
        obj.attr += 1
    else:
        return ('object attribute "attr" have different type')
    return ('plus_one() executed successfully')


def plus_another_one(obj):
    try:
        if type(obj.attr) == int:
            obj.attr += 1
        else: return ('object attribute "attr" have different type')
    except AttributeError:
        return ('object have no attribute "attr"')
    return('plus_another_one() executed successfully')
        

class class1():
    pass

x = class1()
x.abc = 0

y = class1()
y.attr = 0

z = class1()
z.attr = ''


print(f'''{"="*10} Without try-except {"="*10}

{x.__dict__.items()}
{plus_one(x)}
{x.__dict__.items()}

{y.__dict__.items()}
{plus_one(y)}
{y.__dict__.items()}

{z.__dict__.items()}
{plus_one(z)}
{z.__dict__.items()}

{"="*10} With try-except {"="*10}

{x.__dict__.items()}
{plus_another_one(x)}
{x.__dict__.items()}

{y.__dict__.items()}
{plus_another_one(y)}
{y.__dict__.items()}

{z.__dict__.items()}
{plus_another_one(z)}
{z.__dict__.items()}
''')
