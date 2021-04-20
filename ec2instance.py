import boto3
ec2 = boto3.resource('ec2')

# create a new EC2 instance
instances = ec2.create_instances(
     ImageId='ami-05d72852800cbf29e',
     MinCount=1,
     MaxCount=2, #MinCount and MaxCount are used to define the number of EC2 instances to launch. That means if MinCount=1 and MaxCount=3, then 3 instances will be launched. 
     InstanceType='t2.micro',
     KeyName='ec2-keypair'
 )