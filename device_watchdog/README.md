# Monitoring and notifications for LoRaWAN device connection status

This sample contains an example solution for monitoring connectivity status of LoRaWAN devices. It will generate an alarm if AWS cloud does not receive an uplink from a LoRaWAN for longer then a configurable amount of time.

After deploying this solution in your AWS account and performing necessary configuration steps, you will receive an e-mail notificiation each time one of configured LoRaWAN devices is silent for longer then amount of time you defined.  Additionaly, a message will be published to AWS IoT Core message broker MQTT topic (e.g. `awsiotcorelorawan/events/presence/disconnect/<WirelessGatewayId>`) each time LoRaWAN device sends uplink or is silent for longer then amount of time you defined.

## Quick deployment

Please run the following commands in your local shell or in AWS CloudShell.

### **1. Deploy the CDK stack**

``` shell
# Clone the repository 
git clone https://github.com/aws-samples/aws-iot-core-lorawan
cd aws-iot-core-lorawan/device_watchdog
# Set up and activate virtual environment
python3 -m venv .env
source .env/bin/activate 
# Install AWS CDK and neccessary CDK libraries
npm install -g aws-cdk
pip3 install -r requirements.txt   
# If first time running CDK deployment in this account / region, run CDK bootstap
# This is a one-time activity per account/region, e.g. 
# cdk bootstrap aws://123456789/us-east-1
cdk bootstrap aws://<Account Id>/<Region name>
# Deploy the stack. Ensure to replace <E-Mail> with the E-Mail adresss to send notifications to
cdk deploy --parameters emailforalarms=<E-Mail> --parameters notifyifinactivseconds=600
```

### **2. Confirm the SNS e-mail subscription**  

Please check your mailbox for an e-mail message with subject "AWS Notification - Subscription Confirmation" and confirm the subscription.


### **3. Add Action to your AWS IoT Rules**
Please open AWS IoT Rule that processes incoming telemetry from your device. 

**Update IoT SQL statement**
Please ensure that IoT SQL statement of your AWS IoT Rule adds output attributes "timestamp_ms" with current timestamp and "deviceid" with a unique device identification e.g.:

```SQL
SELECT timestamp() as timestamp_ms, WirelessDeviceId as deviceid, ...  
```
**Add action**
Please add Action "Send a message to an IoT Events Input" to the AWS IoT Rule. Please specify `LoRaWANDeviceWatchdogInput` as "Input name" , leave "Message Id" empty and create a new Role for IoT Events access.

### **4. View notifications and MQTT presence events** 

Please open the [MQTT Test client](https://console.aws.amazon.com/iot/home?region=#/test) and subscribe to the topics `awsiotcorelorawan/events/uplink` and `awsiotcorelorawan/events/presence/missingheartbeat/+`.

Once one of LoRaWAN device you configured in Step 3 is silent for longer then the duration you defined, you will see an MQTT message published on `awsiotcorelorawan/events/presence/missingheartbeat/+` topic.

Each time one of LoRaWAN device you configured in Step 3 is ingesting data, you will see an MQTT message published on `awsiotcorelorawan/events/uplink`.

### **5.Remove the stack**

``` 
cd aws-iot-core-lorawan/device_watchdog
cdk destroy
```


## Troubleshooting

### View AWS Step Functions execution trace

1. Open state machine `LoRaWANGatewayWatchdogStatemachine...` [here](https://console.aws.amazon.com/states/home?region=#/statemachines)
2. Click on a recent execution
3. View the execution trace and potential errors

### View AWS IoT Events logs

1. Open AWS IoT Events settings [here](https://console.aws.amazon.com/iotevents/home?region=#/settings/logging)
2. Configure Logging on "DEBUG" level with a debug target as detector model `LoRaWANGatewayConnectivityModel`
3. View the CloudWatch logs for potentially helpful error messages from AWS IoT Events

## Implementation setails

### **AWS IoT Events**
AWS IoT Events Detector model:
![IoT Events Detector model](images/ioteventsdetectormodel.png)

### **AWS Step functions state machine**
![AWS Step functions state machine](images/step_functions_state_machine.png)


## Local testing


### Install SAM CDK (beta)
```
brew install aws-sam-cli-beta-cdk.
```

### Locally invoke AWS Lambda

```
sam-beta-cdk local invoke LorawanConnectivityWatchdogStack/GetWirelessGatewayStatisticsLambda -e tests/input_connected.json
```

```
sam-beta-cdk local invoke LorawanConnectivityWatchdogStack/GetWirelessGatewayStatisticsLambda -e tests/input_disconnected.json
```