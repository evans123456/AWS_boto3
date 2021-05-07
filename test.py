# import http.client

# #curl -d '{"key1":"yezur"}' https://11zwbpoixg.execute-api.us-east-1.amazonaws.com/default/pi_estimator 

# c = http.client.HTTPSConnection("11zwbpoixg.execute-api.us-east-1.amazonaws.com")
# json = '{"key1":"yezur"}'
# c.request("POST", "/default/pi_estimator",json )
# response = c.getresponse()
# data = response.read().decode("utf-8")

# print(data)


# import math

# r=6
# print(math.pi * (r*r))


current_floor = input("Enter current floor: ")
going_floor = input("which floor are you going: ")

print(f" CF: {current_floor},  GF: {going_floor} ")
going_floor = int(going_floor)
current_floor = int(current_floor)

# print(type(going_floor))

floors = going_floor - current_floor
print("Floors moved: ",floors)

if floors > 0:
    print(f"Lift is moving up: {floors}")
else:
    print(f"Lift is moving down: {floors * -1}")