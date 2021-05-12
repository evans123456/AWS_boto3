#  gcloud app logs tail -s default -> see logs
# gcloud app deploy

from flask import Flask, redirect,url_for, render_template, request, jsonify
import queue
import threading
import time
import http.client 
import json
import math
import statistics
from random import random
from concurrent.futures import ThreadPoolExecutor
import ast
from flask_socketio import SocketIO
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

    


app = Flask(__name__)
# socketio = SocketIO(app)
cred = credentials.Certificate("serviceAcc.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

queue = queue.Queue() # queue is synchronized, so caters for multiple threads
# count = 1000
# important = []
max_tries = 2
results=[]



@app.route("/reset")
def reset():
    results = []
    jsonify({'data':results})
    







@app.route('/_get_data', methods=['POST'])
def _get_data():
    global results

    return jsonify({'data':results})




















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




random_decimal = random()

@app.route("/test")
def test():
    return render_template("test.html", x=random_decimal)

@app.route("/update_decimal", methods=["POST"])
def update_decimal():
    random_decimal = random()
    return jsonify("",render_template("test2.html", x=random_decimal))




@app.route("/output/<service>/<R>/<D>/<Q>/<S>")
def output(service,R,D,Q,S):
    eR = int(S)/int(R)
    incircle=0
    shot = 0
    pi_estimations = []
    # print("Each resource: ",eR)
    
    global max_tries,results
    results = []
    pi_values=[]

    if service == "lambda":
        print("LAMBDA")

        # while max_tries >= 0:

        # subbing from here

        # results = getpages(R,D,Q,S) 

        

        # -----------------------------------------------------------------------------------------------------------
        while max_tries > 0:
            with ThreadPoolExecutor() as executor:        
            # results = executor.map(getpage, runs)  
                runs=[value for value in range(int(R))]
        

            for i in runs:
           
                try:  #each R      
                    host = "11zwbpoixg.execute-api.us-east-1.amazonaws.com"        
                    c = http.client.HTTPSConnection(host)        
                    data = {
                        'thread_id': i,
                            "D":D,
                            "Q":Q,
                            "S":eR
                        }  
                    # start = time.time()
                    c.request("POST", "/default/pi_estimator", json.dumps(data))        
                    response = c.getresponse()        
                    # data = response.read().decode('utf-8')        
                    # print( data, " from Thread", id )     

                    data = json.loads(response.read().decode('utf-8') ) 
                    # data.update({'thread_id': i,})   
                    print("here:  ",data)
                    if "errorMessage" in data:
                        print("Error from AWS")
                    else:
                        results.append(data)

                    #ajax here
                    

                except IOError:        
                    print( 'Failed to open ', host ) # Is the Lambda address correct?    
                    print(data+" from "+str(i)) # May expose threads as completing in a different order    
                    return "page "+str(i)


            for i in results:
                print("I ->: ",i)
                # elapsed_time.append(i['elapsed_time'])
                
                for j in ast.literal_eval(i['values']):
                    incircle = j[0] + incircle
                    shot = j[1] + shot
                    pie = (j[0]/j[1]) * 4
                    pi_estimations.append(pie)

                    print("results: ",j)
            
            print(f"Total Incircle: {incircle}, Shots: {shot}")

            pi_estimate = (incircle/shot)*4
            print("PI Estimate: ",pi_estimate)

            truncated_pi_estimate = truncate(pi_estimate, int(D)-1)
            print ("truncated_pi_estimate: ",truncated_pi_estimate)

            # cut pi to size d
            pi_val_to_match = truncate(math.pi, int(D)-1)
            print("pi_val_to_match: ",pi_val_to_match)

            if float(pi_val_to_match) == float(truncated_pi_estimate):#remove + 1
                print("Matches!!!!")
                db.collection("runs").add(
                    {"cost":0.001150369644165039,
                    "d":D,
                    "pi_estimate":pi_estimate,
                    "q":Q,
                    "r":R,
                    "s":S}
                )
                break


                # break
            else:
                print("Dont Match!")
                max_tries = max_tries -1



            
        
    elif service == "ec2":
        print("EC2")

    # print("OUTPUT: ",results)
    return render_template("output.html",pi_estimations=pi_estimations,res=results,incircle=incircle,shot=S,pi_estimate=pi_estimate)


# https://11zwbpoixg.execute-api.us-east-1.amazonaws.com/default/pi_estimator -> request url
# curl -d '{"key1":"yezur"}' https://11zwbpoixg.execute-api.us-east-1.amazonaws.com/default/pi_estimator 

@app.route("/<srvce>/<R>",methods = ["POST","GET"])
def lastPage(srvce, R):
    
    if request.method == "POST":
        S = request.form["number_of_shots"]
        Q = request.form["reporting_rate"]
        D = request.form["matching_digits"]
        print(f"S : {S}, Q: {Q},D : {D}")
        
        return redirect(url_for("output",service=srvce,R=int(R),D=int(D),Q=int(Q),S=int(S)))

    else:
        return render_template("lastpage.html")







@app.route("/history")
def history():
    values = []
    docs = db.collection("runs").get()
    for doc in docs:
        print(doc.to_dict())
        values.append(doc.to_dict())


    return render_template("history.html",vals=values)


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
    # socketio.run(app)
    # app.run(host='0.0.0.0', port=80,debug=True)




# time ?



# @app.route("/test")
# def test():
#     return render_template("test.html", x=random_decimal)

# @app.route("/update_decimal", methods=["POST"])
# def update_decimal():
#     random_decimal = np.random.rand()
#     return jsonify("",render_template("test2.html", x=random_decimal))