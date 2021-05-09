from flask import Flask, redirect,url_for, render_template, request, jsonify
import queue
import threading
import time
import http.client 
import json
import math
import statistics
import numpy as np
from concurrent.futures import ThreadPoolExecutor


app = Flask(__name__)

queue = queue.Queue() # queue is synchronized, so caters for multiple threads
count = 1000
important = []
max_tries = 3
results=[]

class ThreadUrl(threading.Thread):  
    def __init__(self, queue, task_id,D,Q,S):    
        threading.Thread.__init__(self)    
        self.queue = queue    
        self.task_id = task_id    
        self.data = None # need something more sophisticated if the thread can run many times
        self.D = D
        self.Q = Q
        self.S = S
    
    def run(self):    
        #while True: # uncomment this line if a thread should run as many times as it can      
        count = self.queue.get()      
        host = "11zwbpoixg.execute-api.us-east-1.amazonaws.com"      
        try:        
            c = http.client.HTTPSConnection(host)        
            # json= '{ "D": ' + str(D) + '}' 
            data = {
                "D":self.D,
                "Q":self.Q,
                "S":self.S,
            }       
            c.request("POST", "/default/pi_estimator", json.dumps(data))        
            response = c.getresponse()        
            self.data = json.loads(response.read().decode('utf-8') ) 
            self.data.update({'thread_id': self.task_id,})   
            important.append(self.data)
            print("yees", self.data)     
        except IOError:        
            print( 'Failed to open ' , host ) # Is the Lambda address correct?      
            #signals to queue job is done      
            self.queue.task_done()
        self.queue.task_done()
    

def parallel_run(R,D,Q,S):  
    threads=[]  #spawn a pool of threads, and pass them queue instance  
    for i in range(0, R):    
        t = ThreadUrl(queue, i,D,Q,S)    
        threads.append(t)    
        t.setDaemon(True)    
        t.start()  
    
    #populate queue with data  
    for x in range(0, R):    
        queue.put(count) 
    
    #wait on the queue until everything has been processed  
    queue.join() 
    # print("API res: ",json.loads(t.data))

    # [float(json.loads(th.data) )for th in threads]

    results = [float(json.loads(t.data["body"] ))for t in threads]
    print("The results: ",results)
    return results




def executeParralel(R,D,Q,S):
    start = time.time()
    pi_estimations = parallel_run(int(R),int(D),int(Q),int(S))
    elapsed_time = time.time() - start
    print( "Elapsed Time:", elapsed_time)
    return pi_estimations,elapsed_time







def getpage(id,D,Q,S):    
    try:        
        host = "11zwbpoixg.execute-api.us-east-1.amazonaws.com"        
        c = http.client.HTTPSConnection(host)        
        data = {
                "D":D,
                "Q":Q,
                "S":S
            }       
        c.request("POST", "/default/pi_estimator", json.dumps(data))        
        response = c.getresponse()        
        # data = response.read().decode('utf-8')        
        # print( data, " from Thread", id )  

        data = json.loads(response.read().decode('utf-8') ) 
        data.update({'thread_id': id,})   
        print("here:  ",data)
        return data

    except IOError:        
        print( 'Failed to open ', host ) # Is the Lambda address correct?    
        print(data+" from "+str(id)) # May expose threads as completing in a different order    
        return "page "+str(id)

def getpages(R,D,Q,S):    
    with ThreadPoolExecutor() as executor:        
        # results = executor.map(getpage, runs)  
        runs=[value for value in range(int(R))]
    
        for i in runs:
            data=getpage(i,int(D),int(Q),int(S))
            print("getpage_data",data)
            results.append(data)

            # ajax here


        # print("inside the while: ",results)  
    return results






@app.route("/reset")
def reset():
    results = []
    




























def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


@app.route("/",methods = ["POST","GET"])
def home():
    if request.method == "POST":
        # user = request.form["nm"]
        service = request.form["flexRadioDefault"]
        print("The service: ",service)
        return redirect(url_for("resources",srv=service))

        
    else:
        return render_template("home.html")

@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)


random_decimal = np.random.rand()

@app.route("/test")
def test():
    return render_template("test.html", x=random_decimal)

@app.route("/update_decimal", methods=["POST"])
def update_decimal():
    random_decimal = np.random.rand()
    return jsonify("",render_template("test2.html", x=random_decimal))




@app.route("/output/<service>/<R>/<D>/<Q>/<S>")
def output(service,R,D,Q,S):
    global max_tries,results

    if service == "lambda":
        print("LAMBDA")

        # while max_tries >= 0:

        results = getpages(R,D,Q,S) 

        print("OUTPUT: ",results)




            # pi_estimations,elapsed_time = executeParralel(R,D,Q,S) #ignore elapsed time
            # print("PI ESTIMATIONS",pi_estimations)

            # estimated_value_of_pi = statistics.mean(pi_estimations)
            # truncated_value_of_pi = truncate(estimated_value_of_pi, int(D)-1)
            # print ("estimated_value_of_pi: ",estimated_value_of_pi)
            # print ("truncated_value_of_pi: ",truncated_value_of_pi)

            # # cut pi to size d
            # pi_val_to_match = truncate(math.pi, int(D)-1)
            # print("pi_val_to_match: ",pi_val_to_match)

            # if float(pi_val_to_match) == float(truncated_value_of_pi):#remove + 1
            #     print("Matches!!!!")


            #     break
            # else:
            #     print("Dont Match!")
            #     new_pi_estimations,new_elapsed_time = executeParralel(R,D,Q,S)

            #     # need to append the arrays to form one big one
            #     pi_estimations = pi_estimations + new_pi_estimations
            #     print("All Estimations: ",pi_estimations)
            #     print(f"max_tries: {max_tries} After append: {pi_estimations}")
            # max_tries = max_tries - 1
    
        # return render_template("output.html",res=results) 

            
        
    elif service == "ec2":
        print("EC2")

    return render_template("output.html",res=results)


# https://11zwbpoixg.execute-api.us-east-1.amazonaws.com/default/pi_estimator -> request url
# curl -d '{"key1":"yezur"}' https://11zwbpoixg.execute-api.us-east-1.amazonaws.com/default/pi_estimator 

@app.route("/<srvce>/<R>",methods = ["POST","GET"])
def lastPage(srvce,R):
    
    if request.method == "POST":
        S = request.form["number_of_shots"]
        Q = request.form["reporting_rate"]
        D = request.form["matching_digits"]
        print(f"S : {S}, Q: {Q},D : {D}")
        
        return redirect(url_for("output",service=srvce,R=R,D=D,Q=Q,S=S))

    else:
        return render_template("lastpage.html")







@app.route("/history")
def history():
    return render_template("history.html")


@app.route("/<srv>",methods = ["POST","GET"])
def resources(srv):
    if request.method == "POST":

        no_of_resources = request.form["no_of_resource"]
        print("Resources: ",no_of_resources)

        
        
        return redirect(url_for("lastPage",srvce=srv,R=no_of_resources))

        
    else:
        return render_template("resources.html",content=srv)


if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=80,debug=True)




# time ?



# @app.route("/test")
# def test():
#     return render_template("test.html", x=random_decimal)

# @app.route("/update_decimal", methods=["POST"])
# def update_decimal():
#     random_decimal = np.random.rand()
#     return jsonify("",render_template("test2.html", x=random_decimal))