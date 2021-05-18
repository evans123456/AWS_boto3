# curl -d '{"thread_id": 1,"D": 5,"Q": 10000,"S": 200000}' https://11zwbpoixg.execute-api.us-east-1.amazonaws.com/default/my_incircle_and_shot_values 


from flask import Flask, redirect,url_for, render_template, request, jsonify
import queue
import boto3
import http.client 
import json
import math
from random import random
from concurrent.futures import ThreadPoolExecutor
import ast
from flask_socketio import SocketIO
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

    


app = Flask(__name__)

cred = credentials.Certificate("serviceAcc.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

queue = queue.Queue() 


def describe_ec2_instance():
    try:
        print ("Describing EC2 instance")
        resource_ec2 = boto3.client("ec2")
        # print(resource_ec2.describe_instances())
        print(resource_ec2.describe_instances()["Reservations"][0]["Instances"][0]["InstanceId"])
        return str(resource_ec2.describe_instances()["Reservations"][0]["Instances"][0]["InstanceId"])
    except Exception as e:
        print(e)

def truncate(f, digits):
    return ("{:.30f}".format(f))[:-30+digits]

def get_public_ip(instance_id):
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")


    for reservation in reservations:
        for instance in reservation['Instances']:
            print(instance.get("PublicIpAddress"))
    
    return instance.get("PublicIpAddress")

def calculate_cost(time_taken):
    # us-east-ohio
    one_request = 0.20/1000000
    running_cost = time_taken * 0.0000097222
    return one_request + running_cost



@app.route("/",methods = ["POST","GET"])
def home():
    if request.method == "POST":
        service = request.form["flexRadioDefault"]
        return redirect(url_for("resources",srv=service))
        
    else:
        return render_template("home.html")

def create_ec2_instance():
    user_data = '''#!/bin/bash
        sudo apt-get update &&
        sudo apt-get install python3 &&
        sudo apt install python3-pip &&
        Y && 
        sudo apt-get install nginx &&
        Y && 
        git clone https://github.com/evans123456/ec2Flask.git && 
        cd ec2Flask &&
        pip install -r requirements.txt &&
        gunicorn -b 0.0.0.0:8000 app:app  '''





    try:
        print ("Creating one EC2 instance")
        resource_ec2 = boto3.client("ec2",region_name='us-east-1')
        resource_ec2.run_instances(
            ImageId="ami-0d5eff06f840b45e9",
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
            UserData=user_data, 
            KeyName="mypem",
           #security_groups=['coursework_1']
        )
        print("end of request")
    except Exception as e:
        print(e)

@app.route("/shutdownR",methods = ["POST"])
def stop_ec2_instance():
    try:
        print ("Stopping EC2 instance")
        instance_id = describe_ec2_instance()
        resource_ec2 = boto3.client("ec2")
        print(resource_ec2.stop_instances(InstanceIds=[instance_id]))
    except Exception as e:
        print(e)

@app.route("/output/<service>/<R>/<D>/<Q>/<S>/",methods = ["POST","GET"])
def output(service,R,D,Q,S):
    
    
    eR = int(S)/int(R)
    
    max_tries = 3

    if service == "lambda":
        results = []
        total_time=0
        in_sh_vals=[]
        isScalable=0
        incircle=0
        shot = 0
        pi_estimations = []
        times = []
 
        while max_tries > 0:
            with ThreadPoolExecutor() as executor:        
                runs=[value for value in range(int(R))]
        

            for i in runs:
           
                try:     
                    host = "11zwbpoixg.execute-api.us-east-1.amazonaws.com"        
                    c = http.client.HTTPSConnection(host)        
                    data = {
                        'thread_id': i,
                            "D":D,
                            "Q":Q,
                            "S":eR
                        }  
                    c.request("POST", "/default/pi_estimator", json.dumps(data))        
                    response = c.getresponse()        
  

                    data = json.loads(response.read().decode('utf-8') ) 
                    print("From AWS: ",data)
                    if "errorMessage" in data:
                        pass
                    else:
                        results.append(data)

                    

                except IOError:        
                    print( 'Failed to open ', host ) # Is the Lambda address correct?    
                    print(data+" from "+str(i)) # May expose threads as completing in a different order    
                    return "page "+str(i)

            print("results: ",results)
            for i in results:

                times.append(ast.literal_eval(i['elapsed_time']))
                
                for j in ast.literal_eval(i['values']):
                    incircle = j[0] + incircle
                    shot = j[1] + shot
                    pie = (j[0]/j[1]) * 4
                    pi_estimations.append(pie)
                    in_sh_vals.append([i["thread_id"],incircle,shot])

            
            print(incircle,shot)
            pi_estimate = (incircle/shot)*4

            truncated_pi_estimate = truncate(pi_estimate, int(D)-1)

            pi_val_to_match = truncate(math.pi, int(D)-1)

            total_time = sum(times)

            if float(pi_val_to_match) == float(truncated_pi_estimate):#remove + 1
                db.collection("runs").add(
                    {"cost":total_time,
                    "d":D,
                    "pi_estimate":pi_estimate,
                    "q":Q,
                    "r":R,
                    "s":S}
                )
                break


            else:
                max_tries = max_tries -1

        print("OUTPUT: ",pi_estimations)
        return render_template("output.html",total_time=total_time,pi_estimations=pi_estimations,isScalable=isScalable,res=in_sh_vals,incircle=incircle,shot=S,pi_estimate=pi_estimate)



            
        
    elif service == "ec2":
        pi_estimate=0
        isScalable=1
        total_time=0
        pi_estimations=[]
        in_sh_vals=[]
        incircle=[]

        for i in range(0,R):
            create_ec2_instance()
            instance_id = describe_ec2_instance()
            print(type(instance_id))

            public_ip = get_public_ip(instance_id)
            print(type(public_ip))

    
    return render_template("output.html",total_time=total_time,pi_estimations=pi_estimations,isScalable=isScalable,res=in_sh_vals,incircle=incircle,shot=S,pi_estimate=pi_estimate)



@app.route("/<srvce>/<R>",methods = ["POST","GET"])
def lastPage(srvce, R):
    
    if request.method == "POST":
        S = request.form["number_of_shots"]
        Q = request.form["reporting_rate"]
        D = request.form["matching_digits"]
        
        return redirect(url_for("output",service=srvce,R=int(R),D=int(D),Q=int(Q),S=int(S)))

    else:
        return render_template("lastpage.html")







@app.route("/history",methods = ["GET"])
def history():
    items = []
    docs = db.collection("runs").get()
    for doc in docs:
        items.append(doc.to_dict())

    return render_template("history.html",vals=items)


@app.route("/<srv>",methods = ["POST","GET"])
def resources(srv):
    if request.method == "POST":

        no_of_resources = request.form["no_of_resource"]       
        
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