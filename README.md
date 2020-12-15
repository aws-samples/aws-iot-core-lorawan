# AWS IoT Core for LoRaWAN tools and sample applications
AWS IoT Core for LoRaWAN connects sensors with LoRaWAN gateways, allowing for deployed sensors to transmit data directly to the AWS IoT cloud. You can use AWS IoT Core for LoRaWAN to create a fully functional connectivity network, deploy sensors, and transmit the data to the AWS IoT cloud to refine with other services. This repository contains tools and sample applications to support you in building solutions based on AWS IoT Core for LoRaWAN.

- [Getting started: decoding binary payloads and integrating with AWS IoT Core](transform_binary_payload)

    In this sample you will learn how decode binary format of  your LoRaWAN device payloads and integrate the transformed payload with other AWS services by using AWS IoT Rules.

- [How to analyse LoRaWAN payloads with Amazon Timestream and visualize them with Grafana](timestream)

    You can use "AWS IoT Core for LoRaWAN" to ingest time series data from your LoRaWAN devices into Amazon Timestream. After that you can visualize your data in Grafana using a [Grafana timestream plugin](https://grafana.com/grafana/plugins/grafana-timestream-datasource/installation). This repository how to build a sample solution for storing your times eries data and visualizing them.

- [Sample soil moisture alarming application based on AWS IoT Core, AWS IoT Events and Amazon SNS ](soilmoisture_alarming)   
    Detecting events based on telemetry data from connected devices is a common use case in IoT across many industries. This repository contains a sample for integrating AWS IoT Events with LoRaWAN for IoT Core. You can learn how to translate telemetry values from a LoRaWAN device into events and notify users about these events using E-Mail and SMS. 

