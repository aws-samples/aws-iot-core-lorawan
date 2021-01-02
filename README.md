# AWS IoT Core for LoRaWAN sample applications 
AWS IoT Core for LoRaWAN enables you to set up a private LoRaWAN network by connecting your devices and gateways with no LoRaWAN Network Server setup required. This repository contains resources to quickly get started developing solutions using AWS IoT Core for LoRaWAN. It includes samples for typical design patterns ([binary decoder](transform_binary_payload), [downlink messaging](send_downlink_payload), [Thing shadow update](iotthingshadow)) and fully functional applications ([dashboards](timestream), [condition monitoring and alarming](soilmoisture_alarming)).

Please consider our [developer guide](https://docs.aws.amazon.com/iot/latest/developerguide/connect-iot-lorawan.html) to learn how to connect your wireless devices and gateways to AWS IoT Core for LoRaWAN.

## Samples for typical design patterns

- [A "Hello world" application: decoding uplink binary payloads](transform_binary_payload)  
    LoRaWAN devices typically send uplink payloads as binary encoded messages. In this sample you will learn how to decode a binary message from your LoRaWAN device and integrate the decoded payload with more than 17 AWS services.

- [Sending downlink payload to a LoRaWAN device](send_downlink_payload)  
    In this sample you will learn how to implement different options for sending downlink payload to your LoRaWAN devices. It includes examples for AWS SDK, AWS CLI and AWS IoT Core message broker.

- [Updating IoT Thing shadow with decoded device payload](iotthingshadow)  
    AWS IoT Thing [Shadows](https://docs.aws.amazon.com/iot/latest/developerguide/iot-device-shadows.html) can make a device’s state available to apps and other services whether the device is connected to AWS IoT or not. In this sample you will learn how to update the shadow of an AWS IoT Thing with the telemetry from a LoRaWAN device. 

## Fully functionable sample applications

- [Visualizing telemetry and transmission metadata from LoRaWAN devices with Amazon Timestream and Grafana plugin](timestream)  
    In this sample you will learn how to store telemetry from your LoRaWAN Devices as well as transmission metadata (e.g. RSSI and SNR per gateway) into Amazon Timestream. Afterwards you will learn how to visualize time series data in Grafana using a [Grafana plugin for Amazon Timestream](https://grafana.com/grafana/plugins/grafana-timestream-datasource/installation). 

- [Monitoring and alarming of soil moisture by using AWS IoT Core for LoRaWAN and AWS IoT Events](soilmoisture_alarming)  
    Detecting events based on telemetry data from connected devices is a common use case in IoT across many industries. This sample explains how to integrate AWS IoT Events with LoRaWAN for IoT Core. You can learn how to translate telemetry values from a LoRaWAN device into events and notify users about these events using E-Mail and SMS.


## Getting help 
- [API Reference](http://docs.aws.amazon.com/console/iot/wireless/intro/apiref)
- [Developer guide](http://docs.aws.amazon.com/console/iot/wireless/intro/devguide)
- [FAQs](https://aws.amazon.com/iot-core/faqs/#AWS_IoT_Core_for_LoRaWAN)
- [Support forums](https://forums.aws.amazon.com/forum.jspa?forumID=210)
- [Partner catalog](https://devices.amazonaws.com/search?page=1&sv=iotclorawan)
