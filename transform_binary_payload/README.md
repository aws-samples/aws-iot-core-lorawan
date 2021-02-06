# AWS IoT Core for LoRaWAN - transform a binary LoRaWAN payload into JSON

LoRaWAN devices often encode transmitted data in a binary format, as it increases transmission efficiency and improves battery lifetime. However, as the data arrive in the cloud, many use cases require a structured format. Transforming the binary data into JSON, for example, enables filtering and enrichment using [AWS IoT SQL](https://docs.aws.amazon.com/iot/latest/developerguide/iot-sql-reference.html) as well as acting on the data using [AWS IoT Rule Actions](https://docs.aws.amazon.com/iot/latest/developerguide/iot-rule-actions.html).

This repository contains resources for you to learn how to transform binary payloads for your LoRaWAN device. These resources include:

- Binary decoders for a set of devices, which will be deployed in an [AWS Lambda layer](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html) so that it may be used in any of your Python lambda functions. Following binary decoders are included:
  - Decoder simulating a temperature and humidity sensor device. It enables you to test is sample without having a physical LoRaWAN device.
  - Browan Tabs Object Locator
  - Dragino LHT65, LGT92, LSE01, LBT1, LDS01
  - Axioma W1
  - Elsys
  - Globalsat LT-100


- An [AWS IoT Rule](#example-for-transforming-a-lorawan-binary-payload) for transforming incoming LoRaWAN binary payloads and acting on the resulting JSON. In this sample, the IoT Rule uses a [republish action](https://docs.aws.amazon.com/iot/latest/developerguide/republish-rule-action.html) to republish transformed payload to another MQTT topic. You can use a similar approach to customize the rule actions for the requirements of your application.

You can quickly test this sample by [deploying these resources using AWS SAM](#step-1-deploy-the-sample-in-your-aws-account). If you prefer to build your own binary transformation decoder for a LoRaWAN device, please follow this [step-by-step guidance](#how-to-build-and-deploy-a-binary-decoder-for-your-lorawan-device).

## Solution Architecture

A picture bellow illustrates an architecture in this sample:

![Architecture](images/0000-resized.png)

By executing a stack in a CloudFormation template the following resources will be deployed in your AWS account:

- AWS IoT Rule `samplebinarytransform_TransformLoRaWANBinaryPayload_...` with the necessary IAM roles and policies to perform rule actions
- AWS Lambda function `samplebinarytransform-TransformLoRaWANBinaryPayloadFunction...` that will invoke the binary decoder for your device
- AWS Lambda layer `samplebinarytransform-LoRaWANPayloadDecoderLayer...` containing the binary decoder logic
  
The names above assume that `samplebinarytransform` will be the stack name. A name of a binary decoder will be appended to the name of the AWS IoT Rule.

## Example for transforming a LoRaWAN binary payload

Example binary deocoders for the following devices are included in this sample:

| Manufacturer | Device              | Decoder name       |
| ------------ | ------------------- | ------------------ |
| Browan       | Tabs Object Locator | tabs_objectlocator |
| Axioma       | W1                  | axioma_w1          |
| Dragino      | LHT65               | dragino_lht65      |
| Dragino      | LGT92               | dragino_lgt92      |
| Dragino      | LSE01               | dragino_lse01      |
| Dragino      | LBT1                | dragino_lbt1       |
| Dragino      | LDS01               | dragino_lds01      |
| Elsys        | all                 | elsys              |
| Globalsat    | LT-100              | globalsat_lt100    |


Before you proceed, please select a preferred approach for using this sample:

- If you don't have a LoRaWAN device yet, or your LoRaWAN device is not included in a list above, please proceed to [Approach A: using simulated decoder](#approach-a-using-simulated-decoder). You will learn how to use binary decoding based on a decoder for a simulated device.
- If your device is included in the list above, please proceed to [Approach B](#approach-b-using-lorawan-device-with-an-included-decoder). You will get guidelines on how to deploy a binary decoder for your device.


## Approach A: using simulated decoder

### Step 1: Deploy the sample for a simulated decoder in your AWS account


**Note:** The sample requires AWS SAM CLI, you can find installation instructions [here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html). If you use [AWS CloudShell](https://aws.amazon.com/cloudshell/) or [AWS Cloud9](https://aws.amazon.com/cloud9/), SAM is already preinstalled.

Please perform the following steps to deploy a sample application:

1. Check out this repository on your computer

    ```shell
    git clone https://github.com/aws-samples/aws-iot-core-lorawan 
    cd aws-iot-core-lorawan/integration/transform_binary_payload
    ```

2. Perform the following command to build the SAM artifacts:

   ```shell
   sam build
   ```

3. Deploy the SAM template to your AWS account.

   ```shell
   sam deploy --guided --stack-name samplebinarytransform
   ```

    Please select the default values of parameters by typing "Enter", with the following exceptions:
    - Parameter **AWS Region:** select a region supporting AWS IoT Core for LoRaWAN
    
    Please note that `sam deploy --guided` should be only executed for a first deployment. To redeploy after that please use `sam deploy`.

4. Please wait few minutes to complete the deployment

    ```bash
    Successfully created/updated stack - samplebinarytransform in <region>
    ```


### Step 2: Testing binary transformation by simulating an ingestion from a LoRaWAN device

1. Please open the MQTT Test Client in AWS Management console by using [this link](https://console.aws.amazon.com/iot/home?#/test). Please ensure to use the same AWS region that you selected in `sam --deploy-guided` command.
2. Please subscribe to the topic `lorawantransformed`
3. Please publish the payload as specified below to the MQTT topic `$aws/rules/samplebinarytransform_TransformLoRaWANBinaryPayloadFor_sample_device`. 

    ```json
    {
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

4. Please review the messages on the topic `lorawantransformed`
  
    The expected output on the topic `lorawantransformed` should be:

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

The "transformed_payload" part of the message contains artificialy created decoded payload data according to the instructions in the binary decoder you can find in `src-payload-decoders/python/sample_device.py`:
```python
    result = {
        "temperature": temperature,
        "humidity": humidity
    }
```

## Step 3: Integrating with AWS IoT Core for LoRaWAN

After a successful deployment of the AWS CloudFormation stack, you should configure AWS IoT Core for LoRaWAN to invoke AWS IoT Rule `samplebinarytransform_TransformLoRaWANBinaryPayload_sample_device` each time AWS IoT Core receives a message from a LoRaWAN device:

1. Open "IoT Core" in an AWS management console
2. Click on "Wireless connectivity"
3. Click on "Destinations"
4. Click on "Add destination"
5. Configure the new destination:
   - IAM Role : if you have not created the IAM role for invocation of AWS IoT Rule yet, please click [here for guidelines](#how-to-create-an-iam-role-for-aws-iot-core-for-lorawan-destination)
   - DestinationName: for example `SampleDeviceDestination`
   - RuleName: please input `samplebinarytransform_TransformLoRaWANBinaryPayloadFor_sample_device`

6. Click on "Add destination" button at the bottom of the page
7. Please assign the newly created destination `SampleDeviceDestination` to your LoRaWAN device:  
     - If you create a new LoRaWAN device in AWS IoT Core for LoRaWAN, you should specify `SampleDeviceDestination` as a destination
     - If you already have created a LoRaWAN devices, please use the "Edit" function of the console to update the Destination of the device

## Step 4: Verify the invocation of the AWS IoT Rule 

The following description assumes that you already configured and tested your LoRaWAN Device and LoRaWAN gateway in AWS IoT Core for LoRaWAN. To learn how to do this, please consult [AWS IoT Core for LoRaWAN developer guide](https://docs.aws.amazon.com/iot/latest/developerguide/connect-iot-lorawan.html#connect-iot-lorawan-getting-started-overview).

To verify the invocation of the AWS IoT Rule, please follow these steps:
1. Open "IoT Core" in an AWS management console
2. Click on "Test" to open a MQTT client 
3. Click on "Subscribe to topic"
4. Add `lorawantransformed` and click on "Subscribe"
5. Click on "Subscribe to topic"
6. Add `lorawanerror` and click on "Subscribe"
7. Trigger or wait for the ingestion for your LoRaWAN device connected to AWS IoT Core for LoRaWAN
6. After LoRaWAN device ingestion, you should see a payload like this on `lorawantransformed` topic:
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

Congratulations! You successfully implemented and tested binary decoding for AWS IoT Core for LoRaWAN.

Now you can configure the processing of the decoded data by adding further actions to the AWS IoT Rule `samplebinarytransform_TransformLoRaWANBinaryPayload_sample_device`, for example actions to:

- Store the data in Amazon Timestream, DynamoDB or S3
- Send a message as an input to AWS IoT events  
- Send a message to AWS IoT analytics  

After you have completed working with this sample, you can proceed to [Cleaning up](#step-5-cleaning-up) section.


## Approach B: using LoRaWAN device with an included decoder

### Step 1: Deploy the sample 

**Note:** The sample requires AWS SAM CLI, you can find installation instructions [here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html). If you use [AWS CloudShell](https://aws.amazon.com/cloudshell/) or [AWS Cloud9](https://aws.amazon.com/cloud9/), SAM is already preinstalled.

Please perform the following steps to deploy a sample application:

1. Check out this repository on your computer

    ```shell
    git clone https://github.com/aws-samples/aws-iot-core-lorawan 
    cd aws-iot-core-lorawan/transform_binary_payload
    ```

2. Perform the following command to build the SAM artifacts:

   ```shell
   sam build
   ```

3. Deploy the SAM template to your AWS account.

   ```shell
   sam deploy --guided --stack-name samplebinarytransform
   ```

    Please select the default values of parameters by typing "Enter", with the following exceptions:
    - Parameter **AWS Region:** select a region supporting AWS IoT Core for LoRaWAN
    - Parameter **ParamBinaryDecoderName**: select a decoder name according to a following overview:

    | Manufacturer | Device              | Decoder name       |
    | ------------ | ------------------- | ------------------ |
    | Axioma       | W1                  | axioma_w1          |
    | Dragino      | LHT65               | dragino_lht65      |
    | Dragino      | LBT1                | dragino_lbt1       |
    | Dragino      | LSE01               | dragino_lse01      |
    | Dragino      | LGT92               | dragino_lgt92      |
    | Dragino      | LDS01               | dragino_lds01      |
    | Browan       | Tabs Object Locator | tabs_objectlocator |
    | Elsys        | all                 | elsys              |
    | Globalsat    | LT-100              | globalsat_lt100    |
    

  Please note that `sam deploy --guided` should be only executed for a first deployment. To redeploy after that please use `sam deploy`.

4. Please wait few minutes to complete the deployment

    ```bash
    Successfully created/updated stack - samplebinarytransform in <region>
    ```

### Step 2: Testing binary transformation by simulating an ingestion from a LoRaWAN device

1. Please open the MQTT Test Client in AWS Management console by using [this link](https://console.aws.amazon.com/iot/home?#/test). Please ensure to use the same AWS region that you selected in `sam --deploy-guided` command.
2. Please subscribe to the topic `lorawantransformed`
3. Please publish the payload as specified below to the MQTT topic `$aws/rules/samplebinarytransform_TransformLoRaWANBinaryPayloadFor_<Decoder name>`. 

    **Note**: please replace \<Decoder name> in the topic name with a value of the column "Decoder name" from the table above, e.g. samplebinarytransform_TransformLoRaWANBinaryPayload_axioma_w1.
          
    | Manufacturer | Device name         | Sample "PayloadData"                                             |
    | ------------ | ------------------- | ---------------------------------------------------------------- |
    | Axioma       | W1                  | eoFaXxADAAAAwKRZXwMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= |
    | Dragino      | LHT65               | DRoAAAAABNYBLAA=                                                 |
    | Dragino      | LSE01               | AuHtlACmawQPVGM=                                                 |
    | Dragino      | LGT92               | DSEAAAEVCMUGpAA=                                                 |
    | Dragino      | LBT1                | DxwAAAIDQUJCQ0NEREVFRkYwMjcxMjFGNkFDMy0wNTk=                     |
    | Browan       | Tabs Object Locator | Ae48SPbhAgRupmA=                                                 |
    | Elsys        | all                 | MDEwMEUyMDIyOTA0MDAyNzA1MDYwNjAzMDgwNzBENjIxOTAwRTIxOTAwQTM=     |
    | Globalsat    | LT-100              | MDA4MjY0MDI2NERBRDlGQjg4RENENg==                                 |

    The payload is structured in a same way as it will be ingested by AWS IoT Core for LoRaWAN. Please replace the `<Sample PayloadData>` with the value of "Sample PayloadData>" from the following table:


    ```json
    {
        "PayloadData": "<Sample PayloadData>",
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

4. Please review the messages on the topic `lorawantransformed`
  
    The expected output on the topic `lorawantransformed` should be:


    ```json
    {
      "transformed_payload": {
        ...
        values depending on your LoRaWAN device
        ...
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

### Step 3: Integrating with AWS IoT Core for LoRaWAN

After a successful deployment of the AWS CloudFormation stack, you should configure AWS IoT Core for LoRaWAN to invoke AWS IoT Rule `samplebinarytransform_TransformLoRaWANBinaryPayload_<Decoder name>` each time a LoRaWAN device is sending payload:

1. Open "IoT Core" in an AWS management console
2. Click on "Wireless connectivity"
3. Click on "Destinations"
4. Click on "Add destination"
5. Configure the new destination:
   - IAM Role : if you have not created the IAM role for invocation of AWS IoT Rule yet, please click [here for guidelines](#how-to-create-an-iam-role-for-aws-iot-core-for-lorawan-destination)
   - DestinationName: for example `SampleDeviceDestination`
   - RuleName: please input `samplebinarytransform_TransformLoRaWANBinaryPayloadFor_<Decoder name>`

6. Click on "Add destination" button at the bottom of the page
7. Please assign the newly created destination `SampleDeviceDestination` to a LoRaWAN device:  
     - If you create a new LoRaWAN device in AWS IoT Core for LoRaWAN, you should specify `SampleDeviceDestination` as a destination
     - If you already have created a LoRaWAN devices, please use the "Edit" function of the console to update the Destination of the device

## Step 4: Verify the invocation of the AWS IoT Rule on ingestion from a LoRaWAN device

The following description assumes that you already configured and tested your LoRaWAN Device and LoRaWAN gateway in AWS IoT Core for LoRaWAN. To learn how to do this, please consult [AWS IoT Core for LoRaWAN developer guide](https://docs.aws.amazon.com/iot/latest/developerguide/connect-iot-lorawan.html#connect-iot-lorawan-getting-started-overview).

To verify the invocation of the AWS IoT Rule, please follow these steps:
1. Open "IoT Core" in an AWS management console
2. Click on "Test" to open a MQTT client 
3. Click on "Subscribe to topic"
4. Add `lorawantransformed` and click on "Subscribe"
5. Click on "Subscribe to topic"
6. Add `lorawanerror` and click on "Subscribe"
7. Trigger or wait for the ingestion for your LoRaWAN device connected to AWS IoT Core for LoRaWAN
6. After LoRaWAN device ingestion, you should see a payload like this on `lorawantransformed` topic:
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

Congratulations! You successfully implemented and tested binary decoding for AWS IoT Core for LoRaWAN.

Now you can configure the processing of the decoded data by adding further actions to the AWS IoT Rule `samplebinarytransform_TransformLoRaWANBinaryPayload_sample_device`, for example actions to:

- Store the data in Amazon Timestream, DynamoDB or S3
- Send a message as an input to AWS IoT events  
- Send a message to AWS IoT analytics  

## Step 5: Cleaning up
Please open AWS CloudFormation console, select the stack and click on "Delete"

## How to build and deploy a binary decoder for your LoRaWAN device

### Prerequisites

- Install the AWS CLI
- Install the AWS SAM CLI

### Implementation steps

Please perform following steps to implement your own binary transformation model:

1. Check out this repository on your computer

    ```shell
    git clone https://github.com/aws-samples/aws-iot-core-lorawan 
    cd aws-iot-core-lorawan/transform_binary_payload
    ```

2. Review source code of binary transformation for example in [src-payload-decoders/python/sample_device.py](src-payload-decoders/python/sample_device.py) or other decoders available [src-payload-decoders/python](src-payload-decoders/python) . Create a copy of the example, e.g.

    ```shell
    cp src-payload-decoders/sample_device.py src-payload-decoders/python/mymanufacturer_mydevice.py
    ```
  
3. Implement decoding logic in `src-payload-decoders/python/mymanufacturer_mydevice.py`

   Please consider the following guidelines when implementing your binary decoder:
    - Please ensure to keep the name and signature of dict_from_payload function stable and not to modify it. 
    - In case of a failure in decoding, please raise an exception.
    - In case of successfull decoding, please return a JSON object with decoded key/value pairs

    The following example illustrates these guideines:
    ```python
    def dict_from_payload(base64_input: str, fport: int = None):
      # Your code
      if (error): 
        raise Exception("Error description")
      return {"key1":42, "key2": "43"}
    ```
 
4. Edit `src-iotrule-transformation/app.py` and
    1. Add `import mymanufacturer_mydevice.py` 
    2. Add "mymanufacturer_mydevice" value to VALID_PAYLOAD_DECODER_NAMES

5. This sample uses AWS SAM to build and deploy all necessary resources (e.g. AWS Lambda function, AWS IoT Rule, AWS IAM Roles) to your AWS account. Please perform the following commands to build the SAM artifacts:

   ```shell
   sam build
   ```

   As a results, the artifacts for the deployment will be placed in a an `.aws-sam` directory.

6. Deploy the SAM template to your AWS account.

   ```shell
   sam deploy --guided --stack-name samplebinarytransform
   ```

    Please note that `sam deploy --guided --stack-name samplebinarytransform` should be only executed for a first deployment. To redeploy after that please use `sam deploy`.


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

