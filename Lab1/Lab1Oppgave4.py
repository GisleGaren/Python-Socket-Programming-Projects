def jainsall(a):
    teller = 0
    nevner = 0
    for num in a:
        teller = teller + num
    for num in a:
        nevner = nevner + num**2
    JFI = (teller**2)/(len(a)*nevner)    
    return JFI

file = open("values2.txt",'r')
read = file.readlines()
a = []
value = 0

for line in read:
    subarray = line.split() # Splits up each element in the values2.txt file into subarrays, so first line is initially ["7 Mbps"] gets split up into ["7", "Mbps"] = Two elements in a subarray
    if(subarray[1] == "Kbps"):
        KbpsToMbps = float(subarray[0])
        value = KbpsToMbps * 0.0009765625
    else:
        value = float(subarray[0]) 
    a.append(value)
print(a)    

output = jainsall(a)
print('The JFI values of the two throughputs are: ', output)