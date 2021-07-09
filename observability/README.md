# Oservability of LoRaWAN devices and gateways

Here you will find guidelines for implementing oservability of LoRaWAN devices and gateways when using AWS IoT Core for LoRaWAN:
- To learn how to retrieve **LoRaWAN gateway** statistics, please click [here](#how-to-use-aws-iot-core-for-lorawan-apis-to-retrieve-gateway-statistics)
- To learn how to retrieve **LoRaWAN device** statistics, please click [here](#how-to-use-aws-iot-core-for-lorawan-apis-to-retrieve-device-statistics)



## How to use AWS IoT Core for LoRaWAN APIs to retrieve gateway statistics

You can use [GetWirelessGatewayStatistics](https://docs.aws.amazon.com/iot-wireless/2020-11-22/apireference/API_GetWirelessGatewayStatistics.html) to retrieve the information about timestamp of last uplink and the connectivity status of the gateway. The following steps provide an example for an invocation of this API using AWS CLI. Please ensure that [jq tool](https://stedolan.github.io/jq/) is installed before running these steps.

**Step 1: List wireless gateways**

Please run this command to list wireless gateways registred in your AWS account:

```shell
# Set default region
AWS_DEFAULT_REGION=eu-west-1
# Call GetWirelessGatewayStatistics API
aws iotwireless list-wireless-gateways | jq -r '.WirelessGatewayList[] | "\(.Name),\(.Id)"'
```

As an output of this command you will see a list of wireless gateways registred in your AWS account/region, for example:
```
My Gateway 1,a904247a-772b-4aa5-86bc-86bc86bc86bc
My Gateway 2,e1c68458-0ca1-4c62-9b9a-9b9a9b9a9b9a
```

Please select one of the gateway id's (e.g. `a904247a-772b-4aa5-86bc-86bc86bc86bc`)

**Step 2: Retrieve wireless gateway statistics**

Please run the following command to retrieve statistics for the wireless gateway using the previously noted id:

```shell 
aws iotwireless get-wireless-gateway-statistics --wireless-gateway-id a904247a-772b-4aa5-86bc-86bc86bc86bc
```

You will see a timestamp of last uplink and the connectivity status of the gateway as an output:

```json
{
    "WirelessGatewayId": "a904247a-772b-4aa5-86bc-86bc86bc86bc",
    "LastUplinkReceivedAt": "2021-07-09T06:54:13.597698337Z",
    "ConnectionStatus": "Connected"
}
```


## How to use AWS IoT Core for LoRaWAN APIs to retrieve device statistics

You can use [GetWirelessDeviceStatistics](https://docs.aws.amazon.com/iot-wireless/2020-11-22/apireference/API_GetWirelessDeviceStatistics.html) to retrieve the information about timestamp of last uplink and the connectivity status of the gateway. The following steps provide an example for an invocation of this API using AWS CLI. Please ensure that [jq tool](https://stedolan.github.io/jq/) is installed before running these steps.

**Step 1: List wireless gateways**

Please run this command to list wireless gateways registred in your AWS account:

```shell
# Set default region
AWS_DEFAULT_REGION=eu-west-1
# Call GetWirelessGatewayStatistics API
aws iotwireless list-wireless-devices | jq -r '.WirelessDeviceList[] | "\(.Name),\(.Id)"'
```

As an output of this command you will see a list of wireless devices registred in your AWS account/region, for example:
```
Device 1,b81ad383-6d80-43dc-ae0f-e3e4baa9b3bc
Device 2,75495835-5a61-49fd-ab9f-eeb2e7ef77f5
```

Please select one of the wireless device id's (e.g. `75495835-5a61-49fd-ab9f-eeb2e7ef77f5`)

**Step 2: Retrieve wireless device statistics**

Please run the following command to retrieve statistics for the wireless device using the previously noted id:

```shell 
aws iotwireless get-wireless-device-statistics --wireless-device-id 75495835-5a61-49fd-ab9f-eeb2e7ef77f5
```

You will see a timestamp of last uplink and metadata of last LoRaWAN message as an output:

```json
{
    "WirelessDeviceId": "75495835-5a61-49fd-ab9f-eeb2e7ef77f5",
    "LastUplinkReceivedAt": "2021-07-09T07:05:09.533280525Z",
    "LoRaWAN": {
        "DevEui": "a84041d55182720b",
        "FPort": 2,
        "DataRate": 5,
        "Frequency": 867700000,
        "Timestamp": "2021-07-09T07:05:09.533280525Z",
        "Gateways": [
            {
                "GatewayEui": "c0ee40ffff29df10",
                "Snr": 10.25,
                "Rssi": -31.0
            }
        ]
    }
}
```

