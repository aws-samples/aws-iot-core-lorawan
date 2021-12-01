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

# Payload as described in Reference Manual (TBHH100)

## Byte 0
# Sensors status
# Bits [7:0] 
# - 0x00: VOC sensor 
# - 0x08: Temperature and humidity sensor

## Byte 1
# Battery level
# Bits [3:0] unsigned value ν, range 1 – 14; battery voltage in V = (25 + ν) ÷ 10.
# Bits [7:4] RFU

## Byte 2 
# Temperature as measured by sensor
# Bits [6:0] unsigned value τ, range 0 – 127; temperature in °C = τ - 32.
# Bit [7] RFU

## Byte 3
# Relative Humidity as measured by sensor
# Bits [6:0] unsigned value in %, range 0-100. 
#            A value of 127 indicates measurement error.
# Bit [7] RFU

## Byte 4-5
# CO2
# Bits [15:0] 
# Always 0xffff because module has no CO2 sensor

## Byte 6-7
# VOC
# Bits [15:0] 
# Always 0xffff because module has no VOC sensor

import base64
import json

DEBUG_OUTPUT = False


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

    if DEBUG_OUTPUT:
        print(f"Input: {decoded.hex().upper()}")

    # Byte 1
    if (decoded[0] == 0x00):
        status_sensor_type = 'VOC'
    elif (decoded[0] == 0x08):
        status_sensor_type = 'TempHum'
    else:
        status_sensor_type = 'Unknown'

    # Byte 2
    battery = (25 + (decoded[1] & 0b00001111))/10

    # Byte 3
    temp = decoded[2] & 0b01111111 - 32

    # Byte 4 - relative humidity
    RH = int(decoded[3])

    # Bytes 5-6 CO2
    # is always 0xffff
    # Bytes 7-8 VOC
    # is always 0xffff

    # Output
    result = {
        "status_sensor_type": status_sensor_type,
        "battery_value": battery,
        "temp": temp,
        "RH": RH
    }

    if DEBUG_OUTPUT:
        print(f"Output: {json.dumps(result,indent=2)}")

    return result


# Tests
if __name__ == "__main__":
    test_definition = [
        {
            "input_encoding": "base64",
            "input_value": "CAs1Mv////8=",
            "output": {
                "status_sensor_type": 'TempHum',
                "battery_value": 3.6,
                "temp": 21,
                "RH": 50
            }
        }
    ]

    for testcase in test_definition:
        base64_input = None
        if testcase.get("input_encoding") == "base64":
            base64_input = testcase.get("input_value")
        elif testcase.get("input_encoding") == "hex":
            base64_input = base64.b64encode(
                bytearray.fromhex(testcase.get("input_value"))).decode("utf-8")
        output = dict_from_payload(base64_input)
        for key in testcase.get("output"):
            if testcase.get("output").get(key) != output.get(key):
                raise Exception(
                    f'Assertion failed for input {testcase.get("input_value")}, key {key}, expected {testcase.get("output").get(key)}, got {output.get(key)}')
            else:
                print(
                    f'"{testcase.get("input_value")}" : Successfull test for key "{key}", value "{testcase.get("output").get(key)}"')
