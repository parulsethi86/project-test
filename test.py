i=1
a=1
while i<=100:
    if ((a%3 and a%5)==0) :
        a=a+1
    else:
        print(a)
        a=a+1
    i=i+1

m=1

while m<5:
    print("# ",end="")
    n=1
    while n<5:
        print("#",end="")
        n=n+1
    m=m+1