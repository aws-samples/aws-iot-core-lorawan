# Tool for batch device registration

Please note that this tool is intended for use in lab and experimental environment. It is in users responsibility to review and adjust it before using in production environment.

## Tool invocation parameters

```shell
usage: batch_register_lorawan_devices.py [-h] [--verbose] [--dryrun] --region REGION inputfilename

Batch registration of LoRaWAN devices for AWS IoT Core for LoRaWAN

positional arguments:
  inputfilename         Path to CSV file to process

optional arguments:
  -h, --help                    show this help message and exit
  --verbose, -v                  Provide more output
  --dryrun, -d                  Do everything but API calls
  --region REGION, -r REGION    AWS region
```

## Example of usage

### Step 1: identify device profile id

```shell
aws iotwireless list-device-profiles         
```

### Step 2: identify service profile id 

```shell
aws iotwireless list-service-profiles         
```

### Step 3: Build CSV file

You can use `example_device_list.csv` as an example file.

Required columns:

- Type (currently only "LoRaWAN" is supported)
- DevEui
- AppKey
- AppEui
- DeviceProfileId (see Step 1)
- ServiceProfileId (see Step 2)
- DestinationName (must exist before this script runs)
- AuthenticationMethod (allowed values: OtaaV1_0_x)
- Name (see [API doc](https://docs.aws.amazon.com/iot-wireless/2020-11-22/apireference/API_CreateWirelessDevice.html#iotwireless-CreateWirelessDevice-request-Name))
- Description (see [API doc](https://docs.aws.amazon.com/iot-wireless/2020-11-22/apireference/API_CreateWirelessDevice.html#iotwireless-CreateWirelessDevice-request-Description))


Few rules for the file:

- Columns must be separated by `;`
- Header line with above column names is required
- Please note that the specific ordering of columns is NOT required.
- CSV file can also contain additional columns

### Step 4: Run batch registration script

```shell
pip3 install -r requirements.txt     
python3 batch_register_lorawan_devices.py example_device_list.csv --region eu-west-1
```
