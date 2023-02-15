# def defines a function jains with two inputs which will be taken in as strings
def jains(num1, num2):
    input1 = float(num1) # We then parse input1 and input2 into floats
    input2 = float(num2)
    JFI = (input1 + input2)**2/(2*(input1**2 + input2**2))
    return JFI

input1 = input('Write the first throughput value: ')    
input2 = input('Write the second throughput value: ') 
output = jains(input1,input2)
print('The JFI values of the two throughputs are: ', output)