# AWS IoT Core for LoRaWAN - transform a binary LoRaWAN payload into JSON

LoRaWAN devices often encode transmitted data in a binary format. Doing so increases transmission efficiency and improves battery lifetime. However, as the data arrive in the cloud, many use cases require a structured format. Transforming the binary data into JSON, fo example, enables filtering and enrichment using [AWS IoT SQL](https://docs.aws.amazon.com/iot/latest/developerguide/iot-sql-reference.html) as well as acting on the data using [AWS IoT Rule Actions](https://docs.aws.amazon.com/iot/latest/developerguide/iot-rule-actions.html).

This repository contains resources for you to learn how to transform binary payloads for your LoRaWAN device. These resources include:

- Python decoder for a sample device, to be deployed in an [AWS Lambda layer](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html) so that it may be used in any of your Python lambda functions.

- An [AWS IoT Rule](#example-for-transforming-a-lorawan-binary-payload) for transforming incoming LoRaWAN binary payloads and acting on the resulting JSON. In this sample, the IoT Rule uses a [republish action](https://docs.aws.amazon.com/iot/latest/developerguide/republish-rule-action.html) to republish transformed payload to another MQTT topic. You can use a similar approach to customize the rule actions for the requirements of your application.

You can quickly test this sample by [deploying these resources using AWS CloudFormation](#step-1-launch-the-aws-cloudformation-stack). If you want build your own binary transformation routine for an LoRaWAN device, please follow this [step-by-step guidance](#how-to-build-transformation-routine-for-your-lorawan-device).

## Solution Architecture

A picture bellow illustrates an architecture in this sample:

![Architecture](images/0000-1024x542.png)

By executing a stack in a CloudFormation template the following resources will be deployed in your AWS account:

- AWS IoT Rule  `samplebinarytransform_TransformLoRaWANBinaryPayload_sample_device` with the neccessary IAM roles to perform rule actions
- AWS Lambda function `samplebinarytransform-TransformLoRaWANBinaryPayloadFunction...`
- AWS Lambda layer `samplebinarytransform-LoRaWANPayloadDecoderLayer...`
  
The above names are listed under assumption that you will use `samplebinarytransform`as a stack name.

## Example for transforming a LoRaWAN binary payload

Please follow the steps  below to launch a sample solution in your AWS account, integrate it with LoRaWAN for Iot Core and test it.

### Step 1: Launch the AWS CloudFormation stack

[Launch CloudFormation stack in us-east-1](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?stackName=samplebinarytransform&templateURL=https://githubsample-aws-iot-core-lorawan-us-east-1.s3.amazonaws.com/integration/transform_binary_payload_custom/template/cf-template-dontedit.yaml)

[Launch CloudFormation stack in eu-west-1](https://console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacks/create/review?stackName=samplebinarytransform&templateURL=https://githubsample-aws-iot-core-lorawan-us-east-1.s3.amazonaws.com/integration/transform_binary_payload_custom/template/cf-template-dontedit.yaml)

After you have been redirected to the Quick create stack page at the AWS CloudFormation console take the following steps to launch you stack:

- Leave the default values for Stack name
- Capabilities (at the bottom of the page):
  - Check I acknowledge that AWS CloudFormation might create IAM resources with custom names.
  - Check I acknowledge that AWS CloudFormation might require the following capability: CAPABILITY_AUTO_EXPAND
- Create stack
- Wait until the complete stack is created. It should take round about 10 mins for the stack to complete.

In the Outputs section of your stack in the AWS CloudFormation console you find several values for resources that have been created. You can go back at any time to the Outputs section to find these values.


### Step 2: Testing binary transformation by simulating ingestion from a LoRaWAN device

Please use an MQTT Test Client to ingest a following payload to the topic `lorawanbinary`:

```json
{
    "PayloadDecoderName": "sample_device",
    "PayloadData": "y7QKRAGpAQnEf/8=",
    "WirelessDeviceId": "57728ff8-5d1d-4130-9de2-f004d8722bc2",
    "WirelessMetadata": {
      "LoRaWAN": {
        "DataRate": 0,
        "DevEui": "a84041d55182720b",
        "FPort": 2,
        "Frequency": 867900000,
        "Gateways": [
          {
            "GatewayEui": "dca632fffe45b3c0",
            "Rssi": -76,
            "Snr": 9.75
          }
        ],
        "Timestamp": "2020-12-07T14:41:48Z"
      }
    } 
}
```

The expected output on the topic `dt/lorawantransformed` will be:

```json
{
  "transformed_payload": {
    "input_length": 11,
    "input_hex": "CBB60ACB016D010A347FFF",
    "status": 200,
    "WirelessDeviceId": "57728ff8-5d1d-4130-9de2-f004d8722bc2",
    "DevEui": "a84041d55182720b"
  },
  "lns_payload": {
    "WirelessDeviceId": "57728ff8-5d1d-4130-9de2-f004d8722bc2",
    "WirelessMetadata": {
      "LoRaWAN": {
        "DataRate": 0,
        "DevEui": "a84041d55182720b",
        "FPort": 2,
        "Frequency": 867900000,
        "Gateways": [
          {
            "GatewayEui": "dca632fffe45b3c0",
            "Rssi": -76,
            "Snr": 9.75
          }
        ],
        "Timestamp": "2020-12-07T14:41:48Z"
      }
    },
    "PayloadData": "y7QKRAGpAQnEf/8="
  },
  "timestamp": 1607352177425
}
```

The "transformed_payload" part of the message contains the decoded payload data from your LoRaWAN device according to the instructions in the binary decoder you can find in `src-payload-decoders/python/sample_device.py`:
```
result = {
        "input_length": len(decoded),
        "input_hex": decoded.hex().upper(),
}
```

This sample binary decoder is not aware of the specific encoding of your LoRaWAN device. For the sake of demonstration in calculates only length and hexadecimal representation of the LoRaWAN device payload. However you can easily modify this example to decode the binary encoding of your device, as outlined in [this section](#how-to-build-transformation-routine-for-your-lorawan-device).

Additionally you can customize the processing of the decoded data by adding further actions to the AWS IoT Rule `samplebinarytransform_TransformLoRaWANBinaryPayload_sample_device`, for example actions to to:

- Store the data in Amazon Timestream, DynamoDB or S3
- Send a message as an input to AWS IoT events  
- Send a message to AWS IoT analytics  
  
## Step 3: Integrating with AWS IoT Core for LoRaWAN

After a successful deployment of the AWS CloudFormation stack, you should configure AWS IoT Core for LoRaWAN to invoke AWS IoT Rule `samplebinarytransform_TransformLoRaWANBinaryPayload` each time a LoRaWAN device is sending payload:

1. Open "IoT Core" in an AWS management console
2. Click on "Wireless connectivity"
3. Click on "Destinations"
4. Click on "Add destination"
5. Configure the new destination:
   - IAM Role : if you have not created the IAM role for invocation of AWS IoT Rule yet, please click [here for guidelines](#how-to-create-an-iam-role-for-aws-iot-core-for-lorawan-destination)
   - DestinationName: for example `SampleDeviceDestination`
   - RuleName: please input `samplebinarytransform_TransformLoRaWANBinaryPayloadFor_sample_device`

6. Click on "Add destination" button at the bottom of the page
7. Please assign the newly created destination `SampleDeviceDestination` to a LoRaWAN device:  
     - If you create a new LoRaWAN device in AWS IoT Core for LoRaWAN, you should specify `SampleDeviceDestination` as a destination
     - If you already have created a LoRaWAN devices, please use the "Edit" function of the console to update the Destination of the device

## Step 4: Verify the invocation of the AWS IoT Rule on ingestion from a LoRaWAN device
The following description assumes that you already configured and tested your LoRaWAN Device and LoRaWAN gateway in AWS IoT Core for LoRaWAN. To learn how to do this, please consult AWS IoT Core for LoRaWAN documentation.

To verify the invocation of the AWS IoT Rule, please follow these steps:
1. Open "IoT Core" in an AWS management console
2. Click on "Test" to open a MQTT client 
3. Click on "Subscribe to topic"
4. Add `dt/lorawantransformed` and click on "Subscribe"
5. Click on "Subscribe to topic"
6. Add `dt/lorawanerror` and click on "Subscribe"
7. Trigger or wait for the ingestion for your LoRaWAN device connected to AWS IoT Core for LoRaWAN
6. After LoRaWAN device ingestion, you should see a payload like this on `dt/lorawantransformed` topic:
```json
{
  "transformed_payload": {
    "input_length": 11,
    "input_hex": "CBB40A830140010A347FFF",
    "status": 200,
    "WirelessDeviceId": "57728ff8-5d1d-4130-9de2-f004d8722bc2",
    "DevEui": "a84041d55182720b"
  },
  "lns_payload": {
    "WirelessDeviceId": "57728ff8-5d1d-4130-9de2-f004d8722bc2",
    "WirelessMetadata": {
      "LoRaWAN": {
        "DataRate": 0,
        "DevEui": "a84041d55182720b",
        "FPort": 2,
        "Frequency": 867900000,
        "Gateways": [
          {
            "GatewayEui": "dca632fffe45b3c0",
            "Rssi": -89,
            "Snr": 8.25
          }
        ],
        "Timestamp": "2020-12-07T15:27:28Z"
      }
    },
    "PayloadData": "y7QKgwFAAQo0f/8="
  },
  "timestamp": 1607354848824
}
```

Congratulations! You successfully implemnted and tested binary decoding for AWS IoT Core for LoRaWAN.
## Step 5: Cleaning up
Please open AWS CloudFormation console, select the stack and click on "Delete"

## How to build transformation routine for your LoRaWAN device 

### Prerequisites

- Install the AWS CLI
- Install the AWS SAM CLI

### Implementation steps

Please perform following steps to implement your own binary transformation model:

1. Check out this repository on your computer

    ```shell
    git clone https://github.com/aws-samples/aws-iot-core-lorawan 
    cd integration/transform_binary_payload
    ```

2. Review source code of binary transformation for example in [src-payload-decoders/python/sample_device.py](src-payload-decoders/python/sample_device.py). Create a copy of the example, e.g.

  ```
  cp src-payload-decoders/sample_device.py src-payload-decoders/python/myydevice.py
  ```
 
3. Implement decoding logic in `src-payload-decoders/python/mydevice.py`
 
4. Modify `src-iotrule-transformation/app.py` by 
    - Adding `import mydevice.py` 
    - Adding "mydevice" value to VALID_PAYLOAD_DECODER_NAMES

5. This sample uses AWS SAM to build and deploy all necessary resources (e.g. AWS Lambda function, AWS IoT Rule, AWS IAM Roles) to your AWS account. Please perform the following commands to build the SAM artifacts:

   ```shell
   sam build
   ```

   As a results, the artifacts for the deployment will be placed in a an `.aws-sam` directory.

6. Deploy the SAM template to your AWS account.

   ```shell
   sam deploy --guided
   ```

    Please note that `sam deploy --guided` should be only executed for a first deployment. To redeploy after that please use `sam deploy`.

    Congratulations! You successfully deployed your binary transformation logic into your AWS account. Please follow [this guidelines](#step-3-integrating-with-aws-iot-core-for-lorawan) to integrate with AWS IoT Core for LoRaWAN

## How to create an IAM role for AWS IoT Core for LoRaWAN destination

Please use AWS IAM to add an IAM role with the following configuration:

**Trust relationship**  

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "iotwireless.amazonaws.com"
        ]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**Permissions**  
Role permissions will depend on your use-cases, however they should at least contain the permission to publish to an IoT topic:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "iot:Publish"
            ],
            "Resource": [
                "arn:aws:iot:us-east-1:<your account id>:topic/*"
            ]
        }
    ]
}
```

Please adjust the policy according to your use case following a least privilege principle.