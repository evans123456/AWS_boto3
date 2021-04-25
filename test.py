import http.client

#curl -d '{"key1":"yezur"}' https://11zwbpoixg.execute-api.us-east-1.amazonaws.com/default/pi_estimator 

c = http.client.HTTPSConnection("11zwbpoixg.execute-api.us-east-1.amazonaws.com")
json = '{"key1":"yezur"}'
c.request("POST", "/default/pi_estimator",json )
response = c.getresponse()
data = response.read().decode("utf-8")

print(data)