from flask import Flask, redirect,url_for, render_template, request, jsonify
import queue
import threading
import time
import http.client 
import json
import math
import statistics
import numpy as np


app = Flask(__name__)

queue = queue.Queue() # queue is synchronized, so caters for multiple threads
count = 1000


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
            self.data = response.read().decode('utf-8')        
            print( self.data, " from Thread", self.task_id )      
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
    results = [float(json.loads(t.data)["body"] )for t in threads]
    print(results)
    return results

def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


def executeParralel(R,D,Q,S):
    start = time.time()
    pi_estimations = parallel_run(int(R),int(D),int(Q),int(S))
    print( "Elapsed Time:", time.time() - start)
    elapsed_time = time.time() - start
    return pi_estimations,elapsed_time

@app.route("/",methods = ["POST","GET"])
def home():
    if request.method == "POST":
        # user = request.form["nm"]
        service = request.form["flexRadioDefault"]
        print("The service: ",service)
        return redirect(url_for("resources",srv=service))

        
    else:
        return render_template("home.html")



@app.route("/output")
def output():
    return render_template("output.html")


# https://11zwbpoixg.execute-api.us-east-1.amazonaws.com/default/pi_estimator -> request url
# curl -d '{"key1":"yezur"}' https://11zwbpoixg.execute-api.us-east-1.amazonaws.com/default/pi_estimator 

@app.route("/<srvce>/<R>",methods = ["POST","GET"])
def lastPage(srvce,R):
    max_tries = 3
    if request.method == "POST":
        S = request.form["number_of_shots"]
        Q = request.form["reporting_rate"]
        D = request.form["matching_digits"]
        print(f"S : {S}, Q: {Q},D : {D}")

        if srvce == "lambda":
            print("LAMBDA")


            while max_tries > 0:

                pi_estimations,elapsed_time = executeParralel(R,D,Q,S)
                print("PI ESTIMATIONS",pi_estimations)
                estimated_value_of_pi = statistics.mean(pi_estimations)
                truncated_value_of_pi = truncate(estimated_value_of_pi, int(D)-1)
                print ("estimated_value_of_pi: ",estimated_value_of_pi)
                print ("truncated_value_of_pi: ",truncated_value_of_pi)
                # cut pi to size d
                pi_val_to_match = truncate(math.pi, int(D)-1)
                print("pi_val_to_match: ",pi_val_to_match)
                if float(pi_val_to_match) + 1 == float(truncated_value_of_pi):#remove + 1
                    print("Matches!!!!")

                    break
                else:
                    print("Dont Match!")
                    pi_estimations2,elapsed_time2 = executeParralel(R,D,Q,S)

                    # need to append the arrays to form one big one
                    pi_estimations.extend(pi_estimations2)
                    print(f"max_tries: {max_tries} After append: {pi_estimations}")
                    max_tries = max_tries - 1

            
        
        elif srvce == "ec2":
            print("EC2")
        
        return redirect(url_for("output",pi_estimations=pi_estimations,total_time_for_estimations=elapsed_time))

        
    else:
        return render_template("lastpage.html")


random_decimal = np.random.rand()

@app.route("/test")
def test():
    return render_template("test.html", x=random_decimal)

@app.route("/update_decimal", methods=["POST"])
def update_decimal():
    random_decimal = np.random.rand()
    return jsonify("",render_template("test2.html", x=random_decimal))




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




# time ?