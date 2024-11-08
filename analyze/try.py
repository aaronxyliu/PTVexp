import datetime
import time

# print(time.strftime("%H:%M:%S", 1206))
for x in range (0,5):  
    b = "Loading" + "." * x
    print ( f'{x}' * (10-x) + '\n' + f'{x}' * (10-x), end="\r")
    time.sleep(1)
    print ( ' ' * 15, end="\r")

# def convert_to_preferred_format(sec):
#    sec = sec % (24 * 3600)
#    hour = sec // 3600
#    sec %= 3600
#    min = sec // 60
#    sec %= 60
#    return "%02d:%02d:%02d" % (hour, min, sec) 

# n = 100
# print("Time in preferred format :-",convert_to_preferred_format(n))