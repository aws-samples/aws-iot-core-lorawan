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

# Payload as described in Reference Manual (TBOL100)
# Sensors status
# Bit[0] Bit[1] Bit[2] Bit [3] Bit [4] Bit[7:5]
# 1 - button trigger event, 0 - no button trigger event 1 - moving mode, 0 - stationary mode​ (TBD​)
# RFU
# 1 - no GNSS fix, 0 - GNSS fixed
# 1 - GNSS error, 0 - GNSS OK RFU

# Battery level
# Bits [3:0] unsigned value ν, range 1 – 14; battery voltage in V = (25 + ν) ÷ 10.
# Bits [7:4] RFU

# Temperature as measured by on-board NTC
# Bits [6:0] unsigned value τ, range 0 – 127; temperature in °C = τ - 32.
# Bit [7] RFU

# Latitude as last reported by GNSS receiver
# Bits [27:0] signed value φ, range -90,000,000 – 90,000,000; WGS84 latitude in ° = φ ÷ 1,000,000.
# *Note: little-endian format. Bits [31:28] RFU

# Longitude and position accuracy estimate as last reported by GNSS receiver
# Bits [28:0] signed value ​λ​, range -179,999,999 – 180,000,000; WGS84 longitude in ° = ​λ​÷ 1,000,000.
# Bits [31:29] unsigned value ​α​, range 0-7;
# position accuracy estimate in m = 2α​ +2​ (max).
# The value 7 represents an accuracy estimate of worse than 256m.

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
    status_flag_button_triggered = decoded[0] & 0b10000000 != 0
    status_flag_moving_mode = decoded[0] & 0b01000000 != 0
    status_flag_gnss_fix = decoded[0] & 0b00010000 == 0
    status_flag_gnss_error = decoded[0] & 0b00001000 != 0

    # Byte 2
    battery = (25 + (decoded[1] & 0b00001111))/10

    # Byte 3
    temp = decoded[2] & 0b01111111 - 32

    # Bytes 4-7
    lat = decoded[3] | decoded[4] << 8 | decoded[5] << 16 | decoded[6] << 24
    lat = lat / 1000000

    # Bytes 8-11
    long = decoded[7] | decoded[8] << 8 | decoded[9] << 16 | (
        decoded[10] & 0b00001111) << 24
    long = long / 1000000

    position_accuracy = (decoded[10] & 0b11110000) >> 4

    # Output
    result = {
        "status_flag_button_triggered": status_flag_button_triggered,
        "status_flag_moving_mode": status_flag_moving_mode,
        "status_flag_gnss_fix": status_flag_gnss_fix,
        "status_flag_gnss_error": status_flag_gnss_error,
        "battery_value": battery,
        "temp": temp,
        "lat": lat,
        "long": long,
        "position_accuracy": position_accuracy


    }

    if DEBUG_OUTPUT:
        print(f"Output: {json.dumps(result,indent=2)}")

    return result


# Tests
if __name__ == "__main__":
    test_definition = [
        {
            "input_encoding": "base64",
            "input_value": "Ae48SPbhAgRupmA=",
            "output": {
                "status_flag_button_triggered": False,
                "status_flag_moving_mode": False,
                "status_flag_gnss_fix": True,
                "status_flag_gnss_error": False,
                "battery_value": 3.9,
                "temp": 28,
                "lat": 48.36308,
                "long": 10.90714,
                "position_accuracy": 6
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
