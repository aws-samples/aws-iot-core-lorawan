# Sample for workshop "How to build a binary decoder for AWS IoT Core for LoRaWAN"

## Prerequisites

The sample requires SAM CLI, you can find installation instructions [here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html).

## Deployment

Please perform the following steps to deploy a sample application:
   
1. Check out this repository on your computer

    ```shell
    git clone https://github.com/aws-samples/aws-iot-core-lorawan --branch experimental
    cd workshop/binarydecoder
    ```

2. Please review the SAM template [template.yaml](template.yaml) to understand the ressources that will be created in your AWS accoumt.

3. This sample uses [AWS SAM](https://docs.aws.amazon.com/serverless-application-model/index.html) to build and deploy all necessary resources (e.g. AWS Lambda function, AWS IoT Rule, AWS IAM Roles) to your AWS account. Please perform the following commands to build the SAM artifacts:

   ```shell
   sam build
   ```

4. Deploy the SAM template to your AWS account.

   ```shell
   sam deploy --guided
   ```

    You can use the default parameters.

    Please note that `sam deploy --guided` should be only executed for a first deployment. To redeploy after that please use `sam deploy`.

    