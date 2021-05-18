import boto3

ec2 = boto3.resource('ec2')

user_data = '''#!/bin/bash
echo 'test' > /tmp/hello'''

instance = ec2.create_instances(
        ImageId='ami-0d5eff06f840b45e9', 
        MinCount=1, 
        MaxCount=1, 
        KeyName='mypem', 
        # SecurityGroupIds=['sg-abcd1234'], 
        UserData=user_data, 
        InstanceType='t2.nano', 
        # SubnetId='subnet-abcd1234'
    )