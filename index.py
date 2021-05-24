# curl -d '{"thread_id": 1,"D": 5,"Q": 10000,"S": 200000}' https://11zwbpoixg.execute-api.us-east-1.amazonaws.com/default/my_incircle_and_shot_values 
# view logs gcloud app logs tail -s default

from flask import Flask, redirect,url_for, render_template, request, jsonify
import queue
import boto3
import http.client
import time 
import json
import math
from random import random
from concurrent.futures import ThreadPoolExecutor
import ast
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from functools import partial
import paramiko
from paramiko import SSHClient
from boto.manage.cmdshell import sshclient_from_instance


app = Flask(__name__)
cred = credentials.Certificate("serviceAcc.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
queue = queue.Queue() 


#--------------------------------------------------------------------------------------------------------------

user_data = '''#!/bin/bash
sudo apt-get update &&
sudo apt-get install python3 &&
cd /home/ubuntu/ &&
git clone https://github.com/evans123456/ec2 &&
cd ec2'''

aws_access_key_id="AKIASO6YY2CWKF2GGD26",
aws_secret_access_key="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"


def create_ec2_instance():
    global aws_access_key_id,aws_secret_access_key
    try:
        print ("Creating EC2 instance")
        resource_ec2 = boto3.client("ec2",region_name='us-east-1',aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,)
        resource_ec2.run_instances(
            ImageId="ami-09e67e426f25ce0d7", #ubuntu
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
            UserData=user_data, 
            KeyName="mypem",
            
        )
        print("end of request")
    except Exception as e:
        print(e)


def describe_ec2_instance():
    global aws_access_key_id,aws_secret_access_key
    instance_ids = []
    try:
        print ("Describing EC2 instance")
        resource_ec2 = boto3.client("ec2",region_name="us-east-1",aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)
        for i in resource_ec2.describe_instances()["Reservations"]:

            print(i["Instances"][0]["InstanceId"])
            instance_ids.append(i["Instances"][0]["InstanceId"])
        
        print("DONE")

        # print(resource_ec2.describe_instances()["Reservations"][0]["Instances"][0]["InstanceId"])
        return instance_ids
    except Exception as e:
        print(e)

def get_public_ip(instance_id):
    global aws_access_key_id,aws_secret_access_key
    ec2_client = boto3.client("ec2", region_name="us-east-1",aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)
    reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")

    for reservation in reservations:
        for instance in reservation['Instances']:
            print(instance.get("PublicIpAddress"))
            if instance.get("PublicIpAddress") == None:
                continue
            else:    
                return instance.get("PublicIpAddress")

def get_values_from_ec2(host,eR,Q):
    
    # host="100.26.143.241"
    user="ubuntu"
    key=paramiko.RSAKey.from_private_key_file("./mypem.pem")
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # client.load_system_host_keys()
    client.connect(host, username=user,pkey=key)
    stdin, stdout, stderr = client.exec_command(f'cd /home/ubuntu/ && cd ec2/ && python3 pi_estimator.py {int(eR)} {int(Q)}')
    print ("stderr: ", stderr.readlines())

    vals = stdout.readlines()[4]
    print ("output: ", vals)

    return vals

#---------------------------------------------------------------------------------------------------------------
def truncate(f, digits):
    return ("{:.30f}".format(f))[:-30+digits]

def calculate_cost(time_taken):
    # us-east-ohio
    one_request = 0.20/1000000
    running_cost = time_taken * 0.0000097222
    return one_request + running_cost

#------------------------------------------------------------------------------------------------------------

@app.route("/",methods = ["POST","GET"])
def home():
    if request.method == "POST":
        service = request.form["flexRadioDefault"]

        return redirect(url_for("resources",srv=service))
        
    else:
        return render_template("home.html")



@app.route("/shutdownR",methods = ["POST"])
def stop_ec2_instance():
    global aws_access_key_id,aws_secret_access_key
    instance_ids = describe_ec2_instance()
    for i in instance_ids:
        try:
            print ("Stopping EC2 instance {i}")
            # instance_id = describe_ec2_instance()
            resource_ec2 = boto3.client("ec2",region_name="us-east-1",aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)
            resource_ec2.stop_instances(InstanceIds=[i])
            # resource_ec2.terminate(InstanceIds=[i])
            print(f"{i} STOPPED")
        except Exception as e:
            print(e)
    return render_template("shutdown.html",instance_ids=instance_ids)


@app.route("/output/<service>/<R>/<D>/<Q>/<S>/<instance_ip_address>/",methods = ["POST","GET"])
def output(service,R,D,Q,S,instance_ip_address):
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
        
            print("RUNS: ",runs)
            for i in runs:
                
           
                try:    
                    print("ThreadID: ",i) 
                    host = "11zwbpoixg.execute-api.us-east-1.amazonaws.com"        
                    c = http.client.HTTPSConnection(host)      
                    data = {
                        "Q":Q,
                        "S":eR
                    }   
                     
                    c.request("POST", "/default/pi_estimator", json.dumps(data))        
                    response = c.getresponse()        


                    data = json.loads(response.read().decode('utf-8') ) 
                    data["thread_id"] = i
                    print("From AWS: ",data)

                    if "errorMessage" in data:
                        pass
                    else:                       
                        results.append(data)
                        continue

                    

                except IOError:        
                    print( 'Failed to open ', host ) # Is the Lambda address correct?    
                    print(data+" from "+str(i)) # May expose threads as completing in a different order    
                    return "page "+str(i)

            print("length of results: ",len(results))
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

        print("pie values: ",pi_estimations)
        print("total_time: ",total_time)
        print("pi_estimate: ",pi_estimate)

        return render_template("output.html",total_time=total_time,pi_estimations=pi_estimations,isScalable=isScalable,res=in_sh_vals,incircle=incircle,shot=S,pi_estimate=pi_estimate)



            
        
    elif service == "ec2":
        isScalable=1
        incircle_shot = []
        total_elapsed_time = []
        ec2_pi_estimations=[]
        inc = 0
        sh = 0
        


        while max_tries > 0:

            print(ast.literal_eval(instance_ip_address))
            print(instance_ip_address)
            print(type(instance_ip_address))
            

            for i in ast.literal_eval(instance_ip_address):
                if i is not None:
                    print("IP ADDR: ",i)
                    my_values = get_values_from_ec2(i,eR,Q)
                    my_values = ast.literal_eval(my_values)
                    print(type(my_values))
                    print(type(my_values["values"]))
                    
                    total_elapsed_time.append(float(my_values["elapsed_time"]))
                    tt = sum(total_elapsed_time)
                    print("TOTAL TIME TAKEN: ",tt)


                    for j in my_values["values"]:
                        pi_est = (j[0]/j[1]) *4
                        inc = inc + j[0]
                        sh = sh + j[1]
                        incircle_shot.append([i,j[0],j[1]])
                        ec2_pi_estimations.append(pi_est)
            
            fin_pi_estimate = inc/sh * 4 

            print("incircle_shot values: ",incircle_shot)
            print("Total elapsed time: ",tt)
            print("Pi estimations: ",ec2_pi_estimations)

            truncated_pi_estimate = truncate(fin_pi_estimate, int(D)-1)

            pi_val_to_match = truncate(math.pi, int(D)-1)


            if float(pi_val_to_match) == float(truncated_pi_estimate):#remove + 1
                db.collection("runs").add(
                    {"cost":tt,
                    "d":D,
                    "pi_estimate":ec2_pi_estimations,
                    "q":Q,
                    "r":R,
                    "s":S}
                )
                break
            else:
                max_tries = max_tries -1
    
        return render_template("output.html",total_time=tt,pi_estimations=ec2_pi_estimations,isScalable=isScalable,res=incircle_shot,incircle=inc,shot=sh,pi_estimate=fin_pi_estimate)



@app.route("/<srvce>/<R>",methods = ["POST","GET"])
def lastPage(srvce, R):
    current_state = ""
    instance_ip_address = []
    if srvce=="ec2":
        
        
        instance_ids = describe_ec2_instance()
        print(instance_ids)

        ec2 = boto3.resource('ec2',region_name="us-east-1",aws_access_key_id=aws_access_key_id )
        
        
        while current_state != 'ok':
            for status in ec2.meta.client.describe_instance_status()['InstanceStatuses']:
                
                current_state = status['SystemStatus']['Status']
                print("The status: ",current_state)
            time.sleep(10)


        print("EC2s are running",current_state)

    if request.method == "POST":
        
        if srvce == "ec2":
            for instance in instance_ids:
                
                ip_address = get_public_ip(instance)
                instance_ip_address.append(ip_address)
                

            # [x for x in instance_ip_address if x is not None]
            print("The IPs: ",instance_ip_address)


        S = request.form["number_of_shots"]
        Q = request.form["reporting_rate"]
        D = request.form["matching_digits"]
        
        return redirect(url_for("output",service=srvce,R=int(R),D=int(D),Q=int(Q),S=int(S),instance_ip_address=instance_ip_address))

    else:
        return render_template("lastpage.html",srvce=srvce,current_state=current_state)


# def loader():




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
        if srv == "ec2":
            for i in range(0,int(no_of_resources)):
                create_ec2_instance()
        
        print("Finished creating instances")
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