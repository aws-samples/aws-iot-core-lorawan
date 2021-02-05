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
# https://www.nasys.no/wp-content/uploads/PULSE_READER_UM3080.pdf

# This devices uses different ports for different messages
#
#  | fPort | Usage          | Trans |
#  |-------|----------------|-------|
#  |  24   | Status message | ul/   |
#  |  25   | Usage message  | ul/   |
#  |  49   | Config request | dl/ul |
#  |  50   | Configuration  | dl/   |
#  |  51   | Update mode    | dl/   |
#  |  99   | Boot/Debug     | ul/   |


import base64
import json
import helpers

DEBUG_OUTPUT = False


def dict_from_payload(base64_input: str):
    decoded = base64.b64decode(base64_input)

    if DEBUG_OUTPUT:
        print(f"Input: {decoded.hex().upper()}")

    # Get Interface map from byte 0
    interface_map = decoded[0]
    # Get status of digital1 from interface map
    digital1_status_flag = (interface_map & 0b00000001)
    digital1_status = "not sent"
    if digital1_status_flag == 0b00000001:
        digital1_status = "sent"
    # Get status of digital2 from interface map
    digital2_status_flag = (interface_map & 0b00000010)
    digital2_status = "not sent"
    if digital2_status_flag == 0b00000010:
        digital2_status = "sent"
    # Get status of user triggered from interface map
    user_triggered_flag = (interface_map & 0b01000000)
    user_triggered = "no"
    if user_triggered_flag == 0b01000000:
        user_triggered = "yes"

    # Get battery from byte 1
    # This payload field is a complete mess. Do get a correct value in Volts
    # it is necessary to know the battery type that is reported by the device
    # in the boot message.
    # Because this is not possible to implement in the payload decoder itself,
    # this field is just decoded to integer. With this data it is possible to
    # the map the battery type from the device boot message with the corresponding
    # mapping table as described in the payload documentation later on.
    battery = int(decoded[1])

    # Get temperature from byte 2
    temperature = helpers.bin8dec(decoded[2])

    # Get RSSI from byte 3
    rssi = helpers.bin8dec(decoded[3]) * -1

    # Output
    result = {
        "digital1Status": digital1_status,
        "digital2Status": digital2_status,
        "userTriggered": user_triggered,
        "battery": battery,
        "temperature": temperature,
        "rssi": rssi,
    }

    # Get first digital data starting from byte 4
    # At least one of the digital inputs is on "sent" status
    if digital1_status == "sent" or digital2_status == "sent":
        if digital1_status == "sent":
            digital_data = {'digital1': decode_digital_data(decoded, 4)}
        else:
            digital_data = {'digital2': decode_digital_data(decoded, 4)}
        # Add the first digital data to the result
        result.update(digital_data)

    # Get seconds digital data starting from byte 9
    # This is only needed if both digital inputs are on "sent" status
    if digital1_status == "sent" and digital2_status == "sent":
        digital_data = {'digital2': decode_digital_data(decoded, 9)}
        # Add the second digital data to the result
        result.update(digital_data)

    if DEBUG_OUTPUT:
        print(f"Output: {json.dumps(result,indent=2)}")

    return result


def decode_digital_data(decoded, start_byte):
    # Get digital settings from start byte
    settings = decoded[start_byte]
    
    # Get value of digital during reporting from settings
    value = (settings & 0b00000001)

    # Get digital trigger mode from settings
    trigger_mode_flag = (settings & 0b00000010)
    trigger_mode = "disabled"
    if trigger_mode_flag == 0b00000010:
        trigger_mode = "enabled"

    # Get digital trigger alert from settings
    trigger_alert_flag = (settings & 0b00000100)
    trigger_alert = "no"
    if trigger_alert_flag == 0b00000100:
        trigger_alert = "yes"

    # Get digital medium type from settings
    medium_type_flag = (settings & 0b11110000) >> 4
    medium_type = "unknown"
    if medium_type_flag == 0x00:
        medium_type = "n/a"
    elif medium_type_flag == 0x01:
        medium_type = "Pulses"
    elif medium_type_flag == 0x02:
        medium_type = "Water in L"
    elif medium_type_flag == 0x03:
        medium_type = "Electricity in Wh"
    elif medium_type_flag == 0x04:
        medium_type = "Gas in L"
    elif medium_type_flag == 0x05:
        medium_type = "Heat in Wh"

    # Get digital counter from start byte + 4 to 1
    counter = int((decoded[start_byte + 4] << 24) | (decoded[start_byte + 3] << 16) |
                  (decoded[start_byte + 2] << 8) | (decoded[start_byte + 1]))

    # Output
    result = {
        "value": value,
        "triggerMode": trigger_mode,
        "triggerAlert": trigger_alert,
        "mediumType": medium_type,
        "counter": counter,
    }

    return result


# Tests
if __name__ == "__main__":
    test_definition = [
        {
            "input_encoding": "hex",
            "input_value": "43F61A4B120100000020C4090000",
            "output": {
                "digital1Status": "sent",
                "digital2Status": "sent",
                "userTriggered": "yes",
                "battery": 246,
                "temperature": 26,
                "rssi": -75,
                "digital1": {
                    "value": 0,
                    "triggerMode": "enabled",
                    "triggerAlert": "no",
                    "mediumType": "Pulses",
                    "counter": 1
                },
                "digital2": {
                    "value": 0,
                    "triggerMode": "disabled",
                    "triggerAlert": "no",
                    "mediumType": "Water in L",
                    "counter": 2500
                }
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
            if(testcase.get("output").get(key) != output.get(key)):
                raise Exception(
                    f'Assertion failed for input {testcase.get("input_value")}, key {key}, expected {testcase.get("output").get(key)}, got {output.get(key)}')
            else:
                print(
                    f'"{testcase.get("input_value")}": Successfull test for key "{key}", value "{testcase.get("output").get(key)}"')
