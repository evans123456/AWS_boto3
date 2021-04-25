import queue
import threading
import time
import http.client 
import json

# Modified from: http://www.ibm.com/developerworks/aix/library/au-threadingpython/
# and fixed with try-except around urllib call
# 
runs = 5
count = 1000

queue = queue.Queue() # queue is synchronized, so caters for multiple threads

class ThreadUrl(threading.Thread):  
    def __init__(self, queue, task_id):    
        threading.Thread.__init__(self)    
        self.queue = queue    
        self.task_id = task_id    
        self.data = None # need something more sophisticated if the thread can run many times
        self.t_d = []
    
    def run(self):    
        #while True: # uncomment this line if a thread should run as many times as it can      
        count = self.queue.get()      
        host = "11zwbpoixg.execute-api.us-east-1.amazonaws.com"      
        try:        
            c = http.client.HTTPSConnection(host)        
            json= '{ "key1": ' + str(count) + '}'   
            # print(json)     
            c.request("POST", "/default/pi_estimator", json)        
            response = c.getresponse()        
            self.data = response.read().decode('utf-8')        
            print( self.data, " from Thread", self.task_id ) 
            self.t_d.append({self.task_id:self.data})     
        except IOError:        
            print( 'Failed to open ' , host ) # Is the Lambda address correct?      
            #signals to queue job is done      
            self.queue.task_done()
        self.queue.task_done()

# The class definition ends - the function below is outside
# # the class body, so not initially indented
def parallel_run():  
    threads=[]  #spawn a pool of threads, and pass them queue instance  
    for i in range(0, runs):    
        t = ThreadUrl(queue, i)    
        threads.append(t)    
        t.setDaemon(True)    
        t.start()  
        
    
    #populate queue with data  
    for x in range(0, runs):  
        # print(f"X: {x}, Queue: {queue}, Count: {count}")  
        queue.put(count) 
    
    #wait on the queue until everything has been processed  
    queue.join()  
    results = [t.data for t in threads]
    thread_id = [p.t_d for p in threads]
    print("RES: ",results)
    print("thread_id: ",thread_id)

# Not indented
start = time.time()
parallel_run()
print( "Elapsed Time:", time.time() - start)