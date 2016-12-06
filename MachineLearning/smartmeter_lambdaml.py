'''
function to analyze data records and determine if there's an anomaly in the data by checking against
Amazon Machine Learning
'''
from __future__ import print_function
import boto3
import json
import base64

# set up variables
ml_modelId = 'ml-Mr76vJy45wd' # replace with your modelId
# replace with your sns topic ARN
sns_topic_arn = 'arn:aws:sns:us-east-1:129288622091:SmartMeter-SmartMeterSnsTopic-LY1RSPANMYEP'
# define the variance allowed before alerting via SNS
alert_variance = 20.0

# fixed values for us-east-1, as this is one of the regions where ML is available
ml_region = 'us-east-1'
ml_predict_endpoint = 'https://realtime.machinelearning.us-east-1.amazonaws.com'

print('Loading function')
def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))
    # create clients to sns and amazon machine learning
    sns_client = boto3.client('sns')
    ml_client = boto3.client('machinelearning', region_name=ml_region)

    for record in event['Records']:
        # Kinesis data is base64 encoded so decode here, but it's a string
        # debug record
        print(str(record))
        payload = base64.b64decode(record['kinesis']['data'])
        # convert payload string to a dict
        payload_json = json.loads(payload)
        print("Decoded payload: " + payload)
        print("Processing payload against model: " + ml_modelId)
        ml_response = ml_client.predict(
            MLModelId=ml_modelId,
            Record={
                
                'Line': str(payload_json['Line'])
            },
            PredictEndpoint=ml_predict_endpoint
        )
        print("ML response: " + json.dumps(ml_response))
        # figure out if the recorded value is outside of the expected range defined in alert_variance
        if abs(ml_response['Prediction']['predictedValue'] - payload_json['Voltage']) > alert_variance:
            print("Anomaly detected for device: " + payload_json['DeviceID'] + ". Sending SNS alert.")
            sns_response = sns_client.publish(
                TopicArn=sns_topic_arn,
                Message='Anomaly detected at ' + str(payload_json['Line']) + ' for device ' +
                        payload_json['DeviceID'] + ': the variance between the measured Voltage of '
                        + str(payload_json['Voltage']) + ' and the expected battery discharge rate of '
                        + str(ml_response['Prediction']['predictedValue']) +
                        ' is greater than the maximum expected variance of ' + str(alert_variance)
                        + '. This line may need a technician.',
                Subject='Anomaly Detected! Voltage ='+str(payload_json['Voltage']),
            )
    print('Successfully processed {} records.'.format(len(event['Records']))) # log to CWL
    return 'Successfully processed {} records.'.format(len(event['Records']))
