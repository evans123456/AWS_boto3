'''using AWS lambda, we can run our code without caring about the servers. Normally if you want to run your application
you will need virtual machines for that e.g ec2 instance. When we get ec2 instance we normally install python/java and our code runs
above that. Using AWS lamba we excecute the code without worrying about servers.
Lambda is also known as serverless architecture( we are running code on those servers but we are not managing those servers)

Benefits include
- no servers to manage
- better performance executing code via lambda(runs on latest generation computers)
- Auto scales (based on the number of functions comming to the page)
- we only pay when our code executes(not when idle)

Lambda Use cases
- in response to events e.g 
--- file uploaded to s3 -> process the file and store data into dynamo db
--- create thumbnails for images uploaded to s3
--- resize images uploaded to s3
--- transcode images automatically
--- automation of EBS snapshots
- serverless architecture (web dvlpt can be done with lambda help)

current use case. When ec2 service stops we send the instance id email to mngment
lambda will need access to SNS and cloudwatch logs
'''

import boto3

client = boto3.client('lambda')