# How to automate AWS IoT Core for LoRaWAN 
## Prerequisites
The following examples require the following software:
- AWS CLI
- jq

**MacOS installation instructions**

```shell
# Install homebrew (skip this step if already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
# Install jq
brew install jq
# Install AWS CLI (skip this step if AWS CLI is already instsall)
brew instsall awscli@2
```
  

## How to create a gateway
The example below includes steps for creation of new gateway, creation and association of the related IoT Certificates, retrieval of CUPS/LNS server certificates and identification of CUPS/LNS endpoints. The example below use region us-east-1. If you use other region (e.g. eu-west-1), please adjust the command accordingly.

**1. Create a gateway**  

```shell
GATEWAY_ID=$(aws iotwireless create-wireless-gateway --name MyGateway --description "My Gateway description" --lorawan GatewayEui=1122334411224477,RfRegion=EU868 --region us-east-1 | jq -r .Id)
echo "Created gateway with id $GATEWAY_ID"
```

The output of this command will be the gateway id that you will need in step 3.

**2. Create AWS IoT Certificate and keypair**

```shell 
CERTIFICATE_ID=$(aws iot create-keys-and-certificate \
                --set-as-active \
                --certificate-pem-outfile gateway.certificate.pem \
                --public-key-outfile gateway.public_key.pem \
                --private-key-outfile gateway.private_key.pem \
                --region us-east-1 | jq -r .certificateId)
echo "Created certificate with id $CERTIFICATE_ID"                
                                
```

The output of this command will be the certificateId that you will need in step 3

**3. Associate gateway with the certificate**

```shell
aws iotwireless  associate-wireless-gateway-with-certificate --id $GATEWAY_ID --iot-certificate-id $CERTIFICATE_ID --region us-east-1
```

The expected output should be:

```shell
{
    "IotCertificateId": "<Certificate Id from Step 2>"
}
```

**3. Retrieve server certificates for CUPS or LNS endpoints**

The server certificates are used by Basics Station software that runs on a LoRaWAN gateway to verify the identify of the AWS IoT Core for LoRaWAN endpoints. Please note that if your LoRaWAN gateway supports the CUPS protocol, it should be sufficient to only configure the CUPS endpoint and your gateway will retrieve the LNS endpoint via the CUPS protocol. If your LoRaWAN does not support the CUPS protocol, you should download and configure the LNS endpoint certificate.   

To retrieve the CUPS endpoint certificate please run the following command:
```shell  
aws iotwireless get-service-endpoint --service-type CUPS --region us-east-1 | jq -r .ServerTrust > cups_server_trust.pem
```

To retrieve the LNS endpoint certificate please run the following command. 
```shell  
aws iotwireless get-service-endpoint --service-type LNS --region us-east-1 | jq -r .ServerTrust > lns_server_trust.pem
```

**4. Retrieve URIs of CUPS or LNS endpoint**

Please note that if your LoRaWAN gateway supports the CUPS protocol, it should be sufficient to only configure the CUPS endpoint and your gateway will retrieve the LNS endpoint via the CUPS protocol. If your LoRaWAN does not support the CUPS protocol, you should configure the LNS endpoint

To retrieve the CUPS endpoint certificate please run the following command:
```shell  
aws iotwireless get-service-endpoint --service-type CUPS --region us-east-1 | jq -r .ServiceEndpoint 
```

To retrieve the LNS endpoint certificate please run the following command. 
```shell  
aws iotwireless get-service-endpoint --service-type LNS --region us-east-1 | jq -r .ServiceEndpoint 
```


**4. Perform gateway configuration**  
After a successful completion of the steps above, please use the following information to configure your LoRaWAN gateway according the the gateway's user manual:
- **Gateway certificate:** gateway.certificate.pem
- **Gateway private key:** gateway.private_key.pem
- **Serer trust certificates:** cups_server_trust.pem or lns_server_trust.pem
- **Endpoints for CUPS or LNS**