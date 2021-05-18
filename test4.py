#https://medium.com/pablo-perez/using-boto3-to-list-services-under-ecs-ded7b3bac7bd
import boto3

client = boto3.client(
    'ecs',
    aws_access_key_id='AKIASO6YY2CWAAO4Z4JX',
    aws_secret_access_key='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',
    )

# response = client.create_cluster(
#         clusterName="testlist"
#     )

# print("Response: ",response)


response = client.list_services(cluster="testlist",maxResults=100)
print(response['serviceArns'])


# for x in range(0, 5):

#   response = client.create_service(
#     cluster='testlist',   # use your own ECS cluster here
#     serviceName='service%d' %(x),
#     # taskDefinition='console-sample-app-static:1',
#     desiredCount=1,
#     clientToken='%d' %(x),
#     launchType='EC2'
#    )