import json
import math 
import random

incircle = 0
shots = 200000
q = 10000
count = 0
for i in range(1, shots+1):
        random1 = random.uniform(-1.0, 1.0)  
        random2 = random.uniform(-1.0, 1.0)  
        if( ( random1*random1 + random2*random2 ) < 1 ):
            incircle += 1
        if i % int(q) == 0:
            print(i)
            count += 1

print(count)