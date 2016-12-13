#W205 Final Project Instructions
###Title: Cloud-based IOT Server for Energy Savings


###Team Members
Matthew Burke, Jan Forslow, Vyas Swaminathan, Xiao Wu




###A. Project Description
The project is a UC Berkeley iSchool Project in W205 on creating a cloud-based IOT Server. We simulated devices generating SmartMeter data across all “feeder” lines, set up a managed cloud platform through AWS IoT (Internet of Things) to connect the devices, and tested multiple AWS services to gather, process, analyze and act on the simulated data. Services tested include: AWS Lambda, Amazon Kinesis, Amazon S3, Amazon Machine Learning, Amazon DynamoDB, and Amazon Elasticsearch Service with built-in Kibana integration for data visualization. 


###B. Repo Directory
* Final Report - Final report submission
* Progress Report - Progress report submission
* Proposal - Initial project proposal
* Simulator - Python files used to simulate PowerGrid data and stream in AWS Lambda
* Key - Private key for the running EC2 Instance (for instructors’ access only)
* MachineLearning - Python files used to set up lambda
* Json - Json file used to set up policy
* smartmeter_cloudformation.json - Json file used to set up the managed cloud platform




###C. Instructions
Here are instructions on how to set up and run the final project:


## Part 1. Server Setup
** The instructor can use the key provided on GitHub to access the running EC2 instance. The following steps describe how to start from the beginning.**


First, an SSH Keypair needs to be created to access the device simulator EC2 instance.


Then, we used AWS CloudFormation extensively to configure the required AWS resources. The CloudFormation Template was written in JSON (smartmeter_cloudformation.json) and contains setup information for the EC2 instance as well as the different components. 


In the AWS Management Console, go to CloudFormation Management and create a stack using “Upload a template to Amazon S3” and the JSON file written for the SmartMeter project (smartmeter_cloudformation.json). Identify “SmartMeter” as the Stack name, select your key in “KeyName”, and put an email address that will be used when the device sends an alert. Leave all defaults on the Options page, and check the box that says “I acknowledge that AWS CloudFormation might create IAM resources, and click Create.” The environment can take 20-30 minutes to provision completely. 


After the server is setup, we can use terminal to connect to the instance, and clone all files from our project github.

`$ git clone https://username@github.com/jforslow/MIDS-W205_Project.git`
** please replace username **


## Part 2. Create Resources
For the project, we attempted to use the AWS CLI to simplify some of the later steps. The results can be seen on AWS IoT page. In order to do this through CLI, a user needs to be created under IAM and be given full access to EC2, S3 and IoT. We will need the user’s Access Key ID and Secret Access Key. We will also need to find out the region of our server.
For this project, the following information can be used:
```
# Access Key: AKIAIKLMZCMTRNGLTDOA1`
# Secret Access Key: /VA8A34zcQanl0XxLnS5mRm36riaVtCYzuH3btKV
# Region: us-east-1
```


We will need to install AWS CLI and configure using the information above.
`$ pip install awscli`
or 
```
$ sudo pip install awscli --ignore-installed six
$ aws configure
```
Input Access Key, Secret Access Key, Region, and leave Default output format blank.


After the configuration, we will create the resources needed in the AWS IoT console, this includes:
Thing – A logical representation of a device stored in IoT’s Registry. Supports attributes, as well as Device Shadows, which can be used to store device state & define desired state.
Policy – Attached to Certificates to dictate what that Certificate (or rather, a Thing using that certificate) is entitled to do on AWS IoT.
Certificate – Things can communicate with AWS IoT via MQTT, MQTT over WebSockets or HTTPS. MQTT is a machine-to-machine pub-sub protocol well-suited for IoT use cases given its low overhead and low resource requirements. MQTT transmission to your AWS IoT gateway is encrypted using TLS and authenticated using certs you will create.
Rule – Leverages AWS IoT’s Rules Engine to dictate how messages sent from Things to AWS IoT are handled. You will configure rules that send data published to an MQTT topic to a variety of AWS Services.
Create a thing

`$ aws iot create-thing --thing-name "SmartMeter"`


#####Create a policy
Before creating a policy, a JSON file that describes the policy needs to be created first. We created and saved this file as “Json/SmartMeters-policy.json”
```
$ aws iot create-policy --policy-name "SmartMeterPolicy" --policy-document “file://MIDS-W205_Project/Json/SmartMeters-policy.json”
```

#####Attach thing and policy to the certificate
The Cloudformation file has already generated a certificate file. We need to find the arn of the certificate to attach thing and policy.

`$ aws iot list-certificates`

We got a certificate arn as follows:
```
#arn:aws:iot:us-east-1:129288622091:cert/fb190b8fa71d2ee4700a6d9ddb4fe2eab92a95d0c1e5932feaf795fa69d14478
$ aws iot attach-principal-policy --principal "arn:aws:iot:us-east-1:129288622091:cert/fb190b8fa71d2ee4700a6d9ddb4fe2eab92a95d0c1e5932feaf795fa69d14478" --policy-name "SmartMeterPolicy"
$ aws iot attach-thing-principal --thing-name "SmartMeter" --principal "arn:aws:iot:us-east-1:129288622091:cert/fb190b8fa71d2ee4700a6d9ddb4fe2eab92a95d0c1e5932feaf795fa69d14478"
```

#####REST API endpoint
We need to find out the endpoint name to configure the Device Simulator. We do this by running:
`$ aws iot describe-endpoint`
We then use the value to replace hostname in /MIDS-W205_Project/Simulators/settings.py


Start the device simulator
Under the root directory, run:
`$ nohup python MIDS-W205_Project/Simulator/app.py &`




## Part 3. Writing Device Messages to DynamoDB
We will first create a topic rule to connect our device to DynamoDB. We do this through the AWS IoT web interface.
In the AWS IoT Console, create a rule through “Create a Resource”
The following parameters should be entered:

Field | Value
--- | ---
Name | SmartMeterToDynamo
Description | Writing data to DynamoDB
Attribute | *
Topic filter | line/+/SmartMeterData


2. We need to create two actions, one to write the payload to a database table using the timestamp as a range key value, and one to report the status. 
Click the “Choose an action” dropdown menu and select “Insert message into a database table (DynamoDb)”;
Choose the table whose name contains “TimeSeriesTable” in the Table name field;
In the DynamoDB detailed section, enter the following parameters:

Field | Value 
--- | ---
Table Name | \<stack-name>-SmartMeterDynamoTimeSeriesTable
Hash key value | ${topic(2)} 
Range key value | ${timeStampEpoch}
Role name | \<stack-name>-AwsIotToDynamoRole-\<random-number>

Click the “Choose an action” dropdown menu and select “Insert message into a database table (DynamoDb)”;
Choose the table whose name contains “TimeSeriesTable” in the Table name field;
In the DynamoDB detailed section, enter the following parameters:

Field | Value
--- | ---
Table Name | \<stack-name>-SmartMeterDynamoDeviceStatusTable
Hash key value | ${topic(2)}
Range key value | leave empty
Role name | \<stack-name>-AwsIotToDynamoRole-\<random-number>


Click Create.


3. The CloudFormation template already configured a production stage called “prod” in Amazon API Gateway, where an API Invoke URL is generated. The API reads the DynamoDB table and returns devices data in an API GET method.


The project API is 
<https://1ojb5vltmg.execute-api.us-east-1.amazonaws.com/prod>
A JSON format devices data should be seen. You will notice data update by refreshing the page every few seconds.


We can also use command line to verify the API:
```
$ curl https://1ojb5vltmg.execute-api.us-east-1.amazonaws.com/prod
```



## Part 4. Connecting to Amazon Elasticsearch and Kibana
Kibana is an open source data visualization plugin for Elasticsearch. It provides visualization capabilities on top of the content indexed on an Elasticsearch cluster. In order to let Elasticsearch cluster to receive the device data, we need to create a Firehose role action.
In the AWS IoT Console, create a rule through “Create a Resource”
The following parameters should be entered:


Field
Value
Name
SmartMeterToFirehose
Description
leave empty
Attribute
*
Topic filter
line/+/SmartMeterData


2. Click on “Choose an action” and select “Send the message to a real-time data stream that stores to a bucket (Amazon Kinesis Firehose)”, and then select “Amazon Firehose delivery stream” for stream name.


3. Select “\n (newline)” as the separator, and select AWS IAM role to grant AWS IoT Access.  


4. Click on “Add Action” and “Create”.


Now you can go to the AWS Elasticsearch management console and select the SmartMeter Elasticsearch domain under the Dashboards column and then click on the Kibana endpoint to visualize the device data. 






## Part 5. Setting up AWS Machine Learning
The first step is to generate some ML training data. We did that by running the app.py Simulator code modified to as below:

```
#create ML training file
with open('MIDS-W205_Project/Simulator/TrainDataForML.csv','w') as f:
      f.write('Line,Voltage\n')


#This chunk of code below creates a csv file for the ML component of the project
  with open('MIDS-W205_Project/Simulator/TrainDataForML.csv','a') as f:
      f.write(str(out[0])+','+str(out[2])+'\n')
  f.close()
```

Start loop to begin publishing to topic
```
#while True:
for i in range(1,2500):
Changed to 2500 to complete in 25 min
```

The Simulator was run using the same command as before: 

`[ec2-user@ip-10-0-0-21 ~]$ python MIDS-W205_Project/Simulator/app.py`


S3 is holding the created ML training file and we need the S3 bucket name for this purpose from the S3 in AWS Console. In our setup this is:
smartmeter-smartmeters3bucket-bw2opj77j5jo


We upload the file through the Amazon S3 Console. 


We then go to the AWS Machine Learning Console and its Dashboard, selecting Create New and Data Source and ML model.  


In the Input data page, S3 is selected and we type in the S3 bucket name and add "/TrainDataForML.csv" at the end.


Once we have the S3 location inserted, we can Verify and Continue to the next page.


In the Schema page, select Yes for the question "Does the first line in your CSV contain the column names?". Select Continue to the next page. In the Target page, we select the Voltage as the target. In the Row Id page, we leave the setting to No before going to Review step and Continue to create the ML model with default settings (Numerical regression and save 30% of training data to evaluate model with). 


Once Status changes to Completed, we can continue to Create Endpoint at the end of the page to Enable real-time predictions.  We pick up the following data:
* Endpoint URL: <https://realtime.machinelearning.us-east-1.amazonaws.com>
* ML model ID: ev-MReIGLHgyEa


We need to create one Lambda function to attach to the Kinesis Stream and configure it to call the real-time ML endpoint. For this purpose we go to the AWC Lambda Console and clicking on Create a Lambda function and then Configure Triggers. Once there, we click on the square dotter box and scroll down to select Kinesis filling out the fields as below.



In the configure function screen, we configure the following:

Field | Value
--- | ---
Name | ML-Lambda_SmartMeter
Runtime | Python 2.7
Code entry type | Edit Code Inline
Lambda Function Code | Paste in code from smartmeter_lambdaml.py


In line 11 of the function, we change the ml_modeId with the ML ID from above (ev-MReIGLHgyEa).


In line 13 of the function, change the sns_topic_arn to the SNS Topic ARN under the Output part of the CloudFormation (arn:aws:sns:us-east-1:129288622091:SmartMeter-SmartMeterSnsTopic-LY1RSPANMYEP). This data can be found by going to the CloudFormation Console, then click on the stack name and Output. 


For the Role, select Choose an existing Role
For the existing role, select the roles that has "LambdatoMLandSNS" in the name.
Change the timeout to 10 seconds and click Next to continue.


In line 13, we set the alert_variance to 20. This can be narrowed down later when we have a more refined Simulator.


We then click on Create Function to create the lambda function.


Final setup for this test run is to create an IoT rule to place the data into the Kinesis stream. For this purpose we go back to the AWS IoT Console. In the Create a Rule screen, we configure the following as shown below:


Field | Value
--- | ---
Name | SmartMeterML
Attribute | *
Topic Filter | line/+/SmartMeterData
Choose an action | Sends messages to an Amazon Kinesis stream
Stream name | \<Stack Name>-SmartMeterKinesisStream-\<Random>
Partition key | ${topic(2)}
Role Name | \<Stack Name>-AwsIotToKinesisStreamRole-\<Random>

In our case, the Stack Name is SmartMeter. By clicking on Add Action we see that a new action has been added. Click Create to continue. We have completed the necessary steps to enable the data from IoT to be streamed to Kinesis to ML. 


