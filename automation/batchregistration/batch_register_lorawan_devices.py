# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import pandas as pd
import boto3
import json
import logging
import argparse

# Command line arguments
parser = argparse.ArgumentParser(description='Batch registration of LoRaWAN devices for AWS IoT Core for LoRaWAN')
parser.add_argument('inputfilename', type=str,  help='Path to CSV file to process')
# parser.add_argument('--errorfilename', type=str, help='Path to CSV file to store failed registrations', required=True)
parser.add_argument('--verbose', '-v', action='count', default=1, help='Provide more output')
parser.add_argument('--dryrun', '-d', action='count', default=1, help='Do everything but API calls')
parser.add_argument('--region', "-r", type=str, help='AWS region', required=True)
args = parser.parse_args()
args.verbose = 70 - (10*args.verbose) if args.verbose > 0 else 0

# Logging
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# AWS IoT Wireless client
if args.dryrun == 1:
    iotwireless_client = boto3.client('iotwireless', region_name=args.region)
else:
    logger.info("Dry run, not creating wireless devices")




def register_wireless_device(devicerow) -> bool:

    if (devicerow.Type != "LoRaWAN"):
        logger.error("Allowed device types are: LoRaWAN")
        return False;

    if (devicerow.AuthenticationMethod == "OtaaV1_0_x"):
        authentication_data = {
            "AppKey": devicerow.AppKey,
            "AppEui": devicerow.AppEui
        }
    else:
        logger.error(f"Authentication method {devicerow.AuthenticationMethod} not supported, skipping row for device id {devicerow.DeviceId}")
        return False


    create_wireless_device_input = {
                        "Type": devicerow.Type,
                        "Name": devicerow.Name,
                        "Description": devicerow.Description,
                        "DestinationName": devicerow.DestinationName,
                        "LoRaWAN": {
                                'DevEui': devicerow.DevEui,
                                'DeviceProfileId': devicerow.DeviceProfileId,
                                'ServiceProfileId':    devicerow.ServiceProfileId,
                                devicerow.AuthenticationMethod : authentication_data
                            
                }
    }
    logger.info(f"Creating device with DevEui {devicerow.DevEui}")
    logger.debug(f"Creating wireless device with data {json.dumps(create_wireless_device_input, indent=4)}")
    try: 
        if args.dryrun == 1:
            iotwireless_client.create_wireless_device(**create_wireless_device_input)        
    except Exception as e:
        logger.error(f"Error creating wireless device {e}")
        return False
        
    return False    

logger.info(f"Loading input file {args.inputfilename}")
df = pd.read_csv(args.inputfilename, delimiter=';', quotechar='|')
df_failed = pd.DataFrame().reindex_like(df)

success_count = 0
failure_count = 0

for device_row in df.itertuples(index=False, name="DeviceRow"):
    logger.info(f"Adding device with data {device_row}")
    if register_wireless_device(device_row)         :
        success_count += 1
    else:
        failure_count += 1
#        df_failed.append(pd.Series(device_row), ignore_index=True)
        
    
logger.info("Successfully added {} devices, failed to add {} devices".format(success_count, failure_count))

# if failure_count > 0:
#    logger.info("Writing list of failed devices to {}".format(args.errorfilename))
#    df_failed.to_csv(args.errorfilename, sep=';', index=True)   