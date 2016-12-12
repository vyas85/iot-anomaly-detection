"""
Modify these values to match your configuration
"""
# AWS IoT endpoint settings
HOST_NAME = "akiivb3cx1ocl.iot.us-east-1.amazonaws.com" # replace with your AWS IoT endpoint for your region
HOST_PORT = 8883 # leave this as-is
# thing certs & keys
PRIVATE_KEY = "certs/private.pem.key" # replace with your private key name
DEVICE_CERT = "certs/certificate.pem.crt" # replace with your certificate name
ROOT_CERT = "certs/root-ca.pem"
QOS_LEVEL = 0 # AWS IoT supports QoS levels 0 & 1 for MQTT sessions
# PowerGrid settings
# um_lines, voltage, drop, devices):
NUM_LINES = 20
BASE_VOLTAGE = 123
BASE_DROP = 1
NUM_DEVICES = 40
