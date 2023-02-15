def jainsall(a):
    teller = 0
    nevner = 0
    for num in a:
        teller = teller + num
    for num in a:
        nevner = nevner + num**2
    JFI = (teller**2)/(len(a)*nevner)    
    return JFI

a = [1, 3, 8, 2, 11, 7, 3, 4, 7]
output = jainsall(a)
print('The JFI values of the two throughputs are: ', output)