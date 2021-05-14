def greet():
    print("Hello")
    print("Good Morning")

def add(x,y):
    c = x + y
    d=x-y
    return c,d

greet()
result1,result2 = add(3,4)
print(result1,result2)

def update(x):
    print(id(x))
    x = 8
    print(id(x))

    print(x)

a = 5
print(id(a))
update(a)
print(a)

def person(name,age=6):
    print(name)
    print(age)

person(age=28,name='navin')
person('parul',35)
person('sara')

def sum(a, *b):
    #c = a+b
    print(a)
    print(b)
    c = a
    for i in b:
        c = c + i
    print(c)

sum(4,6,16)

def person(name, **data):
    print(name)
    print(data)
    for i,j in data.items():
        print(i,j)

person('parul',age=35 ,city='va',number=7039849587)

## Count and even numbers passes as a list
def count(lst):
    even=0
    odd=0
    for i in lst:
        if i%2==0:
            even=even+1
        else:
            odd=odd+1
    return even,odd

lst = [2,3,4,5,6,23,4,55,9,7,11]
even, odd = count(lst)
print(even,odd)

print("Event: {} and Odd: {}".format(even,odd))

## Lambda Function

f = lambda a : a*a
f2 = lambda a,b : a+b
result = f(5)
result2 = f2(2,3)
print(result2)
print(result)

from calc import *

c = add(2,31)
print(c)

s = sub(5-2)
print(s)GM
