#!/usr/bin/env python3
# 
import time
import json
import http.client
from concurrent.futures import ThreadPoolExecutor# creates a list of values as long as the number of things we want# in parallel so we could associate an ID to each

parallel = 5
runs=[value for value in range(parallel)]

def getpage(id):    
    try:        
        host = "11zwbpoixg.execute-api.us-east-1.amazonaws.com"        
        c = http.client.HTTPSConnection(host)        
        data = {
                "D":2,
                "Q":1000,
                "S":100000
            }       
        c.request("POST", "/default/pi_estimator", json.dumps(data))        
        response = c.getresponse()        
        # data = response.read().decode('utf-8')        
        # print( data, " from Thread", id )  

        data = json.loads(response.read().decode('utf-8') ) 
        data.update({'thread_id': id,})   
        print("here:  ",data)

    except IOError:        
        print( 'Failed to open ', host ) # Is the Lambda address correct?    
        print(data+" from "+str(id)) # May expose threads as completing in a different order    
        return "page "+str(id)

def getpages():    
    with ThreadPoolExecutor() as executor:        
        results = executor.map(getpage, runs)  
        print("inside the while: ",results)  
    return results


if __name__ == '__main__':    
    start = time.time()    
    results = getpages()    
       
    for result in results:  # uncomment to see results in ID order    #     
        print(result)
    
    print( "Elapsed Time: ", time.time() - start)