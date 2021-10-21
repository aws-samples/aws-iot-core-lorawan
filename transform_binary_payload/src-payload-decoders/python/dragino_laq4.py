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


import base64


def dict_from_payload(base64_input: str, fport: int = None):
    """ Decodes a base64-encoded binary payload into JSON.
            Parameters 
            ----------
            base64_input : str
                Base64-encoded binary payload
            fport: int
                FPort as provided in the metadata. Please note the fport is optional and can have value "None", if not provided by the LNS or invoking function. 

                If  fport is None and binary decoder can not proceed because of that, it should should raise an exception.

            Returns
            -------
            JSON object with key/value pairs of decoded attributes

        """

    decoded = base64.b64decode(base64_input)

    # Battery voltage
    battery_value = ((decoded[0] << 8 | decoded[1]) & 0x3FFF) / 1000
        
    mode=(decoded[2] & 0b01111100)>>2
    
    if mode == 1:               #mode = 1 #for Normal Operation
        Work_mode="CO2"
        if (decoded[2] & 0b00000001):
            Alarm_status = "TRUE"
        else:
            Alarm_status = "FALSE"
            
        TVOC_ppb= decoded[3]<<8 | decoded[4] 
        CO2_ppm= decoded[5]<<8 | decoded[6]
        
        # sensor temperature
        if (decoded[7] & 0b1000000):
            temperature = ((decoded[7] << 8 | decoded[8]) - 0xFFFF)/10
        else:
            temperature = (decoded[7] << 8 | decoded[8])/10
        
        # Humidity
        humidity = ((decoded[9] << 8 | decoded[10])/10)
        
        result = {
        "battery_value": battery_value,
        "work_mode": Work_mode,
        "alarm_status": Alarm_status,
        "TVOC_ppb": TVOC_ppb,
        "CO2_ppm": CO2_ppm,
        "temperature": temperature,
        "humidity": humidity,
        }
    elif mode == 31:            #mode = 31 #for Test
        work_mode="ALARM"
        temperature_min= decoded[3]<<24>>24
        temperature_max= decoded[4]<<24>>24
        humidity_min= decoded[5]
        humidity_max= decoded[6]
        CO2_min= decoded[7]<<8 | decoded[8]
        CO2_max= decoded[9]<<8 | decoded[10] 
        result = {
        "battery_value": battery_value,
        "work_mode": work_mode,
        "temperature_min": temperature_min,
        "temperature_max": temperature_max,
        "humidity_min": humidity_min,
        "humidity_max": humidity_max,
        "CO2_min": CO2_min,
        "CO2_max": CO2_max,
        }
    else:
        raise Exception("Invalid Sensor Mode")
    return result


