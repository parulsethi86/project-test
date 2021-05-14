import sys as s
x = int(s.argv[1])
y = int(s.argv[2])
z = int(s.argv[3])

if x>y:
    if x>z:
        print("x is largest")
elif y>z:
        print("y is largest")
else:
    print("z is largest")

