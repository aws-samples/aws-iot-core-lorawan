# Lambda - Low Power Payload Decoder for AWS IoT Core of LoRaWAN

LoRaWAN devices typically support small message payload sizes. Sensor data is usually binary packed and Base64 encoded. A commonly used format is the [Cayenne Low Power Payload](https://github.com/myDevicesIoT/CayenneLPP)

This project implements a Lambda that can be triggered using an IoT rule to decode the Cayenne Low Power Payload (LPP).

The Lambda handler was tested using packets sent by [Sodaq Explorer](https://support.sodaq.com/Boards/ExpLoRer/) boards with [Grove](https://wiki.seeedstudio.com/Grove_System/) sensors. The data was encoded using this [Arduino library](https://github.com/ElectronicCats/CayenneLPP).

## Message Format

The section below outlines the LoRaWAN packet, the encoded payload and the decoded output as an example.

### Incoming event to Lambda

The message below shows the incoming event to this Cayenne LPP decoder Lambda function.

```bash

{ 
   WirelessDeviceId: '342da222-0be1-45ee-b90d-999144a63e6c',
  PayloadData:
   'AQAuAmUD/wNmAAZnAJsEaE4FcyZ6B3ECLv2R/cAIhgB3/2YAHAmIBSuf8x/1AEUuCYgFK5/zH/UARS4JiAUrn/Mf9QBFLg==',
  WirelessMetadata:
   { LoRaWAN:
      { DataRate: '3',
        DevEui: '0004a30b001b2188',
        FPort: 3,
        Frequency: '903900000',
        Gateways: [Array],
        Timestamp: '2021-02-23T15:29:12Z' 
      } 
   } 
}
```

### Cayenne LPP Encoded Payload

The Cayenne LPP encoded data is the following field in the message. Please note that this sample payload is using the Digital Input field of the Cayenne LPP format to send a packet counter. The packet counter starts at 0, counts up to 255, and then resets back to 0.

```bash

AQAuAmUD/wNmAAZnAJsEaE4FcyZ6B3ECLv2R/cAIhgB3/2YAHAmIBSuf8x/1AEUuCYgFK5/zH/UARS4JiAUrn/Mf9QBFLg==

```

### Decoded Packet Output

```bash
{ 
   timestamp: 1614094153085,
   DevEUI: '0004a30b001b2188',
   DeviceId: '0004a30b001b2188',
   datetime: '2021-02-23T15:29:12Z',
   count: 46,
   lux: 1023,
   presence: 0,
   humidity: 39,
   pressure: 985,
   temperature: 15.5,
   accel: { x: 0.558, y: -0.623, z: -0.576 },
   gyro: { x: 1.19, y: -1.54, z: 0.28 },
   loc: { lat: 33.8847, lng: -84.3787, alt: 177.1 }
}

```

The fields count, lux, presence, humidity, pressure, temperature, accel, gyro, and loc are the ones decoded from the LoRaWAN payload.

The code will have to be adapted for any changes that your packet format may have or key names being used in the message format.
