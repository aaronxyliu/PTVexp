l = [1,2,5,6,3,9]

x = [sorted(l, reverse=True).index(x)+1 for x in l]
print(x)