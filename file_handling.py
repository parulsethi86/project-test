"""file = open('Data_File','r')

#print(file.read())
print(file.readline(),end="")
print(file.readline())
print(file.readline(4)) # read 4 characters

f1 = open('abc','w')
f1.write("Something")
f1.write("Append")
f1.write('laptop')


f1 = open('abc','a')
f1.write("Mobile")
"""
## Copy data_file to abc
f = open('Data_File','r')
f1 = open('abc','w')
for data in f:
    f1.write(data)
#for data in f:
#    print(data)



