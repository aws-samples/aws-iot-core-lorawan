# AWS IoT Core for LoRaWAN sample applications 
AWS IoT Core for LoRaWAN enables customers to connect wireless devices that use low-power, long-range wide area network (LoRaWAN) technology and leverage the richness of AWS platform to build solutions based on the data ingested from these LoRaWAN devices.  Using AWS IoT Core for LoRaWAN, enterprises can setup a private LoRaWAN network by connecting their own LoRaWAN devices to the AWS Cloud - without developing or operating a LoRaWAN Network Server (LNS).

This repository contains fully functional sample applications to help you get started with AWS IoT Core for LoRaWAN.

- [How to decode LoRaWAN device binary payloads and process them with AWS IoT Core and other AWS services](transform_binary_payload)  
    In this sample you will learn how to decode binary format of your LoRaWAN device payloads and integrate the decoded payload with other AWS services by using AWS IoT Rules.

- [How to analyse LoRaWAN payloads with Amazon Timestream and visualize them with Grafana](timestream)  
    You can use AWS IoT Core for LoRaWAN and AWS IoT Core to ingest time series data from your LoRaWAN devices into Amazon Timestream. Once your data are stored in Amazon Timestream, you can visualize your data in Grafana using a [Grafana timestream plugin](https://grafana.com/grafana/plugins/grafana-timestream-datasource/installation). This repository explains how to build a sample solution for storing your times series data and visualizing them.

- [How to implement soil moisture monitoring and alarming solution by using AWS IoT Core for LoRaWAN and AWS IoT Events](soilmoisture_alarming)   
    Detecting events based on telemetry data from connected devices is a common use case in IoT across many industries. This repository contains a sample for integrating AWS IoT Events with LoRaWAN for IoT Core. You can learn how to translate telemetry values from a LoRaWAN device into events and notify users about these events using E-Mail and SMS. 

