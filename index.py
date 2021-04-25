from flask import Flask, redirect,url_for, render_template, request
import queue
import threading
import time
import http.client 
import json



app = Flask(__name__)

queue = queue.Queue() # queue is synchronized, so caters for multiple threads
count = 1000


class ThreadUrl(threading.Thread):  
    def __init__(self, queue, task_id):    
        threading.Thread.__init__(self)    
        self.queue = queue    
        self.task_id = task_id    
        self.data = None # need something more sophisticated if the thread can run many times
    
    def run(self):    
        #while True: # uncomment this line if a thread should run as many times as it can      
        count = self.queue.get()      
        host = "11zwbpoixg.execute-api.us-east-1.amazonaws.com"      
        try:        
            c = http.client.HTTPSConnection(host)        
            json= '{ "key1": ' + str(count) + '}'        
            c.request("POST", "/default/pi_estimator", json)        
            response = c.getresponse()        
            self.data = response.read().decode('utf-8')        
            print( self.data, " from Thread", self.task_id )      
        except IOError:        
            print( 'Failed to open ' , host ) # Is the Lambda address correct?      
            #signals to queue job is done      
            self.queue.task_done()
        self.queue.task_done()


def parallel_run(R):  
    threads=[]  #spawn a pool of threads, and pass them queue instance  
    for i in range(0, R):    
        t = ThreadUrl(queue, i)    
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
    if request.method == "POST":
        s = request.form["number_of_shots"]
        q = request.form["reporting_rate"]
        d = request.form["matching_digits"]
        print(f"S : {s}, Q: {q},D : {d}")
        if srvce == "lambda":
            print("LAMBDA")
            start = time.time()
            pi_estimations = parallel_run(int(R))
            print( "Elapsed Time:", time.time() - start)
            elapsed_time = time.time() - start
            print(pi_estimations)
            
        
        elif srvce == "ec2":
            print("EC2")
        
        return redirect(url_for("output",pi_estimations=pi_estimations,total_time_for_estimations=elapsed_time))

        
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




# time ?