import boto3
import botocore
from operator import is_not
from functools import partial
import paramiko
from paramiko import SSHClient
from boto.manage.cmdshell import sshclient_from_instance

# from boto3 import Session

# session = Session()
# credentials = session.get_credentials()
# # Credentials are refreshable, so accessing your access key / secret key
# # separately can lead to a race condition. Use this to get an actual matched
# # set.
# current_credentials = credentials.get_frozen_credentials()

# # I would not recommend actually printing these. Generally unsafe.
# print(current_credentials.access_key)
# print(current_credentials.secret_key)
# print(current_credentials)


user_data = '''#!/bin/bash
sudo apt-get update &&
sudo apt-get install python3 &&
cd /home/ubuntu/ &&
git clone https://github.com/evans123456/ec2 &&
cd ec2'''


def create_ec2_instance():
    try:
        print ("Creating EC2 instance")
        resource_ec2 = boto3.client("ec2",region_name='us-east-1',aws_access_key_id="AKIASO6YY2CWKF2GGD26",
            aws_secret_access_key="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",)
        resource_ec2.run_instances(
            ImageId="ami-09e67e426f25ce0d7",#ami-0d5eff06f840b45e9
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
    instance_ids = []
    try:
        print ("Describing EC2 instance")
        resource_ec2 = boto3.client("ec2")
        for i in resource_ec2.describe_instances()["Reservations"]:

            print(i["Instances"][0]["InstanceId"])
            instance_ids.append(i["Instances"][0]["InstanceId"])
        
        print("DONE")

        # print(resource_ec2.describe_instances()["Reservations"][0]["Instances"][0]["InstanceId"])
        return instance_ids
    except Exception as e:
        print(e)

def stop_ec2_instance(instance_id):
    try:
        print ("Stopping EC2 instance")
        # instance_id = describe_ec2_instance()
        resource_ec2 = boto3.client("ec2")
        resource_ec2.stop_instances(InstanceIds=[instance_id])
        print(f"{instance_id} STOPPED")
    except Exception as e:
        print(e)

def get_public_ip(instance_id):
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")

    for reservation in reservations:
        for instance in reservation['Instances']:
            print(instance.get("PublicIpAddress"))
            if instance.get("PublicIpAddress") == None:
                continue
            else:    
                return instance.get("PublicIpAddress")


def get_values_from_ec2(host):
    
    # host="100.26.143.241"
    user="ubuntu"
    key=paramiko.RSAKey.from_private_key_file("./mypem.pem")
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # client.load_system_host_keys()
    client.connect(host, username=user,pkey=key)
    stdin, stdout, stderr = client.exec_command(f'cd /home/ubuntu/ && cd ec2/ && python3 pi_estimator.py {200000} {10000}')
    print ("stderr: ", stderr.readlines())

    vals = stdout.readlines()[4]
    print ("output: ", vals)

    return vals

# for i in [1,2,3]:
#     create_ec2_instance()

instance_ids = describe_ec2_instance()
print(instance_ids)

instance_ip_address = []

for instance in instance_ids:
    ip_address = get_public_ip(instance)
    instance_ip_address.append(ip_address)

# [x for x in instance_ip_address if x is not None]
print("The IPs: ",instance_ip_address)


for i in instance_ip_address:
    if i is not None:
        my_values = get_values_from_ec2(i)
        print(my_values)


for i in instance_ids:
    stop_ec2_instance(i)