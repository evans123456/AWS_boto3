import boto3
import botocore
import paramiko
from boto.manage.cmdshell import sshclient_from_instance


user_data = '''#!/bin/bash
git clone <> && cd <directory> &&   '''


def create_ec2_instance():
    try:
        print ("Creating EC2 instance")
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


def describe_ec2_instance():
    try:
        print ("Describing EC2 instance")
        resource_ec2 = boto3.client("ec2")
        # print(resource_ec2.describe_instances())
        print(resource_ec2.describe_instances()["Reservations"][0]["Instances"][0]["InstanceId"])
        return str(resource_ec2.describe_instances()["Reservations"][0]["Instances"][0]["InstanceId"])
    except Exception as e:
        print(e)

def get_public_ip(instance_id):
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")


    for reservation in reservations:
        for instance in reservation['Instances']:
            print(instance.get("PublicIpAddress"))
    
    return instance.get("PublicIpAddress")

# def execute_commands_on_linux_instances(client, commands, instance_ids):
#     """Runs commands on remote linux instances
#     :param client: a boto/boto3 ssm client
#     :param commands: a list of strings, each one a command to execute on the instances
#     :param instance_ids: a list of instance_id strings, of the instances on which to execute the command
#     :return: the response from the send_command function (check the boto3 docs for ssm client.send_command() )
#     """

#     resp = client.send_command(
#         DocumentName="AWS-RunShellScript", # One of AWS' preconfigured documents
#         Parameters={'commands': commands},
#         InstanceIds=instance_ids,
#     )
#     return resp



create_ec2_instance()
# instance_id = describe_ec2_instance()
# print(type(instance_id))

# public_ip = get_public_ip(instance_id)
# print(type(public_ip))


# client = boto3.client('ssm', region_name='eu-west-1')

# params={
#     'command': ['ls'],
#     'username': ['newUser'],
# }

# response = client.send_command(
#     InstanceIds=["i-06468ab9601bc358d",],
#     DocumentName='ResetVpnMfa',
#     DocumentVersion='1',
#     TimeoutSeconds=30,
#     Comment='VPN MFA reset for some.user via Boto',
#     Parameters=params
# )



# client = paramiko.SSHClient()
# # print(client)
# client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# key = paramiko.RSAKey.from_private_key_file("./mypem.pem")
# # print(key)



# # Connect/ssh to an instance
# try:
#     # Here 'ubuntu' is user name and 'instance_ip' is public IP of EC2
#     client.connect("ec2-3-88-231-190.compute-1.amazonaws.com", username="newUser", pkey=key)
#     print("after conect")

#     # Execute a command(cmd) after connecting/ssh to an instance
#     stdin, stdout, stderr = client.exec_command(['echo "hello world"'])
#     print (stdout.read(),stdin, stdout, stderr)

#     # close the client connection once the job is done
#     client.close()

# except Exception as e:
#         print(e)
