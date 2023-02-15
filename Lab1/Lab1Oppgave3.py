def jainsall(a):
    teller = 0
    nevner = 0
    for num in a:
        teller = teller + num
    for num in a:
        nevner = nevner + num**2
    JFI = (teller**2)/(len(a)*nevner)    
    return JFI

file = open("values.txt",'r')
read = file.readlines()
a = []

for line in read:
    subarray = line.split()
    value = float(subarray[0])
    a.append(value)
print(a)    

output = jainsall(a)
print('The JFI values of the two throughputs are: ', output)