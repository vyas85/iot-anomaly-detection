#### Leverages the AWS IoT SDK for Python

# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
#import settings
from settings import *  # importing configuration file
from powergrid import PowerGrid  # importing PowerGrid simulator file
import time
import random
import string
import json
import datetime

# Initialize PowerGrid to settings in settings.py file
grid = PowerGrid(NUM_LINES, BASE_VOLTAGE, BASE_DROP, NUM_DEVICES)



# Update this to new topic?
SMARTMETER_TOPIC = "line/+/SmartMeterData"  # subscribe to wildcard device_id

# Create a random 8-character string for connection id
CLIENT_ID = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))

# Not sure if we want to do this instead of making adjustments within the powergrid automatically?
# Could configure it to adjust based on feedback from kinesis or whatever

# def on_message(client, userdata, msg):
#     # CURRENT_COLOR = new_color()
#     # print(CURRENT_COLOR+"ALERT: Received message on topic "+msg.topic+" with payload: "+str(msg.payload))
#     # print("ALERT: Received message on topic "+msg.topic+" with payload: "+str(msg.payload))
#     name =  msg.topic.split('/')[1]
#     print("ALERT: Received message on topic "+msg.topic+" to recharge device: " + name)
#     # loop through device list to recharge the correct device
#     for x in devs:
#         if x.name == msg.topic.split('/')[1]:
#             x.recharge_device_battery()

#function to convert grid outputs into json payloads
def get_payload(line,hops,voltage, status,modifier,deviceid):
    lat = 35.929673
    lon = -78.948237
    timeStampEpoch = int(time.time() * 1000)  # update timestamp
    timeStampIso = datetime.datetime.isoformat(datetime.datetime.now())
    return json.dumps({"Line": line, "Hops":hops , "Modifier":modifier,"DeviceID": deviceid, "Voltage": voltage, "Status": status, "timeStampEpoch": timeStampEpoch,"timeStampIso":timeStampIso, "location": {"lat": lat, "lon": lon}})



# create AWS IoT MQTT client
client = AWSIoTMQTTClient(CLIENT_ID)

# configure client endpoint / port information & then set up certs
client.configureEndpoint(HOST_NAME, HOST_PORT)
client.configureCredentials(ROOT_CERT, PRIVATE_KEY, DEVICE_CERT)

# configure client connection behavior
client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
client.configureDrainingFrequency(2)  # Draining: 2 Hz
client.configureConnectDisconnectTimeout(10)  # 10 sec
client.configureMQTTOperationTimeout(5)  # 5 sec


# Client subscription needs
print("Connecting to endpoint " + HOST_NAME)
client.connect()
#print("Subscribing to " + SMARTMETER_TOPIC)
#client.subscribe(SMARTMETER_TOPIC, 1, on_message)

'''
#create ML training file
with open('MIDS-W205_Project/Simulator/TrainDataForML.csv','w') as f:
        f.write('Line,Voltage\n')
'''

# start loop to begin publishing to topic
#while True:
for i in range(1,500): # 500 for 5 min run


# (0, 1, 122.59035312697337, 'bdda906d-ff31-4f87-bdd4-0269add37674', 'Normal', 0)
# line, device, voltage, device id, status, modifier
    out = grid.update()
    # Print is correct, can use it to modify client.publish
    print("Line: " + str(out[0]) + " | Hops: " + str(out[1])+ " | Voltage: " + str(round(out[2], 3)) +
          " | Status: " + out[4] + " | Modifier: " + str(out[5]) + " | DeviceID: " + out[3])
    # Not totally sure how to set up this next line..
    client.publish("line/" + str(out[0]) + "/SmartMeterData", get_payload(line = out[0],hops = out[1],voltage = out[2],deviceid = out[3],status = out[4],modifier= out[5]), 0)

    '''
    #This chunk of code below creates a csv file for the ML component of the project
    with open('MIDS-W205_Project/Simulator/TrainDataForML.csv','a') as f:
        f.write(str(out[0])+','+str(out[2])+'\n')
    f.close()
    '''

    time.sleep(0.5)  # wait 0.5 sec before publishing next message.



client.disconnect()
