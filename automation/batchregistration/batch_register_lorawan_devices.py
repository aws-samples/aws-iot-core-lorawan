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

iotwireless_client = boto3.client('iotwireless')
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def register_wireless_device(devicerow) -> bool:

    if (devicerow.AuthenticationMethod == "OtaaV1_0_x"):
        authentication_data = {
            "AppKey": devicerow.AppKey,
            "AppEui": devicerow.AppEui
        }
    else:
        logger.error(f"Authentication method {devicerow.AuthenticationMethod} not supported, skipping row for device id {devicerow.DeviceId}")
        return False


    create_wireless_device_input = {
                        "Type":"LoRaWAN",
                        "Name": device_row.Name,
                        "Description": device_row.Description,
                        "DestinationName": device_row.DestinationName,
                        "LoRaWAN": {
                                'DevEui': devicerow.DevEui,
                                'DeviceProfileId': devicerow.DeviceProfileId,
                                'ServiceProfileId':    devicerow.ServiceProfileId,
                                device_row.AuthenticationMethod : authentication_data
                            
                }
    }
    logger.info(f"Creating wireless device with data {json.dumps(create_wireless_device_input, indent=4)}")
    try: 
        iotwireless_client.create_wireless_device(**create_wireless_device_input)        
    except Exception as e:
        logger.error(f"Error creating wireless device {e}")
        return False
        
    return True    


df = pd.read_csv("devices_list.csv", delimiter=';', quotechar='|')

success_count = 0
failure_count = 0

for device_row in df.itertuples():
    logger.info(f"Adding device {device_row}")
    if register_wireless_device(device_row)         :
        success_count += 1
    else:
        failure_count += 1
    
logger.info("Successfully added {} devices, failed to add {} devices".format(success_count, failure_count))
