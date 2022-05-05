# Example for batch device registration

Please note that this example is intended for use in lab and experimental environment. It is in users responsibility to review and adjust it before using in production environment.

## Step 1: identify device profile id

```shell
aws iotwireless list-device-profiles         
```

## Step 2: identify service profile id 

```shell
aws iotwireless list-service-profiles         
```

## Step 3: Build CSV file

Required columns:

- DevEui
- AppKey
- AppEui
- DeviceProfileId (see Step 1)
- ServiceProfileId (see Step 2)
- DestinationName (must exist before this script runs)
- AuthenticationMethod (allowed values: OtaaV1_0_x)
- Name
- Description

## Step 4: Run batch registration script

```shell
pip3 install -r requirements.txt     
python3 batch_register_lorawan_devices.py
```
