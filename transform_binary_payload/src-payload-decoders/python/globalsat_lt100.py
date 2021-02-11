# Copyright IoT Systems GmbH (www.iot-systems.at). All Rights Reserved.
# Affiliate of KaWa commerce GmbH, AWS Consulting Partner (www.kawa-commerce.com)
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


# Payload definition can be found here
# https://docs.microshare.io/assets/pdf/Globalsat%20LT-100%20format%20.pdf


import base64
import json
import helpers

DEBUG_OUTPUT = False

#   | byte |  bit7  |  bit6  | bit5 | bit4 | bit3 | bit2 | bit1 | bit0 |
#   |------|--------|--------|------|------|------|------|------|------|
#   |   0  |   Device type                                             |
#   |------|-----------------------------------------------------------|
#   |   1  |   GPS fix       |            Report type                  |
#   |------|-----------------------------------------------------------|
#   |   2  |   Battery capacity [%]                                    |
#   |------|-----------------------------------------------------------|
#   |   3  |   Latitude [0.000001 degree]                              |
#   |   4  |                                                           |
#   |   5  |                                                           |
#   |   6  |                                                           |
#   |------|-----------------------------------------------------------|
#   |   7  |   Longitude [0.000001 degree]                             |
#   |   8  |                                                           |
#   |   9  |                                                           |
#   |  10  |                                                           |
#
#
#   |  Device type  | reserved                              |
#   |---------------|---------------------------------------|
#   |  GPS fix      | 00=not fix, 01=2D, 10=3D              |
#   |---------------|---------------------------------------|
#   |  Report type  | 2=Periodic mode report                |
#   |               | 4=Motion mode static report           |
#   |               | 5=Motion mode moving report           |
#   |               | 6=Motion mode static to motion report |
#   |               | 7=Motion mode moving to static report |
#   |               | 14=SOS alarm report                   |
#   |               | 15=Low battery alarm report           |
#   |               | 17=Power on(temperature)              |
#   |               | 19=Power off(low battery)             |
#   |               | 20=Power off(temperature)             |


def dict_from_payload(base64_input: str, fport: int = None):
    decoded = base64.b64decode(base64_input)

    if DEBUG_OUTPUT:
        print(f"Input: {decoded.hex().upper()}")

    # Get device type from byte 0
    device_type = decoded[0]

    # Get gps fix from byte 1, bit 6-7
    gps_fix_flag = (decoded[1] & 0b11000000) >> 6
    gps_fix = "unknown"
    if gps_fix_flag == 0b00:
        gps_fix = "not fix"
    elif gps_fix_flag == 0b01:
        gps_fix = "2D"
    elif gps_fix_flag == 0b10:
        gps_fix = "3D"

    # Get report type from byte 1, bit 0-5
    report_type_flag = (decoded[1] & 0b00111111)
    report_type = "unknown"
    if report_type_flag == 2:
        report_type = "Periodic mode report"
    elif report_type_flag == 4:
        report_type = "Motion mode static report"
    elif report_type_flag == 5:
        report_type = "Motion mode moving report"
    elif report_type_flag == 6:
        report_type = "Motion mode static to motion report"
    elif report_type_flag == 7:
        report_type = "Motion mode moving to static report"
    elif report_type_flag == 14:
        report_type = "SOS alarm report"
    elif report_type_flag == 15:
        report_type = "Low battery alarm report"
    elif report_type_flag == 17:
        report_type = "Power on (temperature)"
    elif report_type_flag == 19:
        report_type = "Power off (low battery)"
    elif report_type_flag == 20:
        report_type = "Power off (temperature)"

    # Get battery capacity from byte 2
    battery_capacity = int(decoded[2])

    # Get latitude from byte 3-6
    lat = ((decoded[3] << 24) | (decoded[4] << 16) |
           (decoded[5] << 8) | (decoded[6]))
    lat = helpers.bin32dec(lat) / 1000000

    # Get longitude from byte 7-10
    long = ((decoded[7] << 24) | (decoded[8] << 16) |
            (decoded[9] << 8) | (decoded[10]))
    long = helpers.bin32dec(long) / 1000000

    # Output
    result = {
        "deviceType": device_type,
        "gpsFix": gps_fix,
        "reportType": report_type,
        "batteryCapacity": battery_capacity,
        "lat": lat,
        "long": long
    }

    if DEBUG_OUTPUT:
        print(f"Output: {json.dumps(result,indent=2)}")

    return result


# Tests
if __name__ == "__main__":
    test_definition = [
        {
            "input_encoding": "hex",
            "input_value": "0082640264DAD9FB88DCD6",
            "output": {
                "deviceType": 0,
                "gpsFix": "3D",
                "reportType": "Periodic mode report",
                "batteryCapacity": 100,
                "lat": 40.164057,
                "long": -74.916650
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
                    f'"{testcase.get("input_value")}": Successfull test for key "{key}", value "{testcase.get("output").get(key)}"')
