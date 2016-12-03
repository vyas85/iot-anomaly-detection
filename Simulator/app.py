#### Leverages the AWS IoT SDK for Python

# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from settings import *  # importing configuration file
from powergrid import PowerGrid  # importing PowerGrid simulator file
import time
import random
import string


# Initialize PowerGrid to settings in settings.py file
grid = PowerGrid(NUM_LINES, BASE_VOLTAGE, BASE_DROP, NUM_DEVICES)


# Update this to new topic?
RECHARGE_ALERT_TOPIC = "device/+/rechargeAlert"  # subscribe to wildcard device_id

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

# create AWS IoT MQTT client
client = AWSIoTMQTTClient(CLIENT_ID)

# configure client endpoint / port information & then set up certs
client.configureEndpoint(settings.HOST_NAME, settings.HOST_PORT)
client.configureCredentials(settings.ROOT_CERT, settings.PRIVATE_KEY, settings.DEVICE_CERT)

# configure client connection behavior
client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
client.configureDrainingFrequency(2)  # Draining: 2 Hz
client.configureConnectDisconnectTimeout(10)  # 10 sec
client.configureMQTTOperationTimeout(5)  # 5 sec


# Client subscription needs
print("Connecting to endpoint " + settings.HOST_NAME)
client.connect()
print("Subscribing to " + RECHARGE_ALERT_TOPIC)
client.subscribe(RECHARGE_ALERT_TOPIC, 1, on_message)

# start loop to begin publishing to topic
while True:


# (0, 1, 122.59035312697337, 'bdda906d-ff31-4f87-bdd4-0269add37674', 'Normal', 0)
# line, device, voltage, device id, status, modifier
    out = grid.update()
    # Print is correct, can use it to modify client.publish
    print("Line: " + str(out[0]) + " | Hops: " + str(out[1])+ " | Voltage: " + str(round(out[2], 3)) +
          " | Status: " + out[4] + " | Modifier: " + str(out[5]) + " | DeviceID: " + out[3])
    # Not totally sure how to set up this next line..
    client.publish("line/" + out[0] + "/devicePayload", dev.get_payload(), settings.QOS_LEVEL)

    time.sleep(5)  # just wait a sec before publishing next message
