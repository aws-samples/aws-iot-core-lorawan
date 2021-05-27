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
# https://www.lairdconnect.com/documentation/application-note-rs1xx-lora-protocol

import base64
import json

import helpers

# DEBUG MODE
DEBUG_OUTPUT = False


#   Send Temp RH Data Notification
#   | byte |  bit7  |  bit6  | bit5 | bit4 | bit3 | bit2 | bit1 | bit0 |
#   |------|--------|--------|------|------|------|------|------|------|
#   |   0  |   MsgType                                                 |
#   |------|-----------------------------------------------------------|
#   |   1  |   Options                                                 |
#   |------|-----------------------------------------------------------|
#   |   2  |   Humidity Fractional                                     |
#   |------|-----------------------------------------------------------|
#   |   3  |   Humidity Integer                                        |
#   |------|-----------------------------------------------------------|
#   |   4  |   Temp Fractional                                         |
#   |------|-----------------------------------------------------------|
#   |   5  |   Temp Integer                                            |
#   |------|-----------------------------------------------------------|
#   |   6  |   Battery Capacity                                        |
#   |------|-----------------------------------------------------------|
#   |   7  |   AlarmMsg Count                                          |
#   |   8  |                                                           |
#   |------|-----------------------------------------------------------|
#   |   9  |   BacklogMsg Count                                        |
#   |  10  |                                                           |

#   Send Battery Voltage
#   | byte |  bit7  |  bit6  | bit5 | bit4 | bit3 | bit2 | bit1 | bit0 |
#   |------|--------|--------|------|------|------|------|------|------|
#   |   0  |   MsgType                                                 |
#   |------|-----------------------------------------------------------|
#   |   1  |   Options                                                 |
#   |------|-----------------------------------------------------------|
#   |   2  |   Voltage Fractional                                      |
#   |------|-----------------------------------------------------------|
#   |   3  |   Voltage Integer                                         |


def dict_from_payload(base64_input: str, fport: int = None):
    """ Decodes a base64-encoded binary payload into JSON.
        Parameters
        ----------
        base64_input : str
            Base64-encoded binary payload
        fport: int
            FPort as provided in the metadata. Please note the fport is optional and can have value "None", if not
            provided by the LNS or invoking function.
            If  fport is None and binary decoder can not proceed because of that, it should should raise an exception.
        Returns
        -------
        JSON object with key/value pairs of decoded attributes
    """

    decoded = base64.b64decode(base64_input)

    # Printing the debug output
    if DEBUG_OUTPUT:
        print(f"Input: {decoded.hex().upper()}")

    if len(decoded):
        # Dict for result
        result = {}

        # Type of message
        msg_type = decoded[0]

        # Sensor to server message options
        options = decoded[1]
        result["options"] = "Undefined"

        sensor_req_server_time = options & 0b00000001
        if sensor_req_server_time == 0b1:
            result["options"] = "Sensor request for server time"

        sensor_config_error = (options & 0b00000010) >> 1
        if sensor_config_error == 0b1:
            result["options"] = "Sensor configuration error"

        sensor_alarm_flag = (options & 0b00000100) >> 2
        if sensor_alarm_flag == 0b1:
            result["options"] = "Sensor alarm flag"

        sensor_reset_flag = (options & 0b00001000) >> 3
        if sensor_reset_flag == 0b1:
            result["options"] = "Sensor reset flag"

        sensor_fault_flag = (options & 0b00010000) >> 4
        if sensor_fault_flag == 0b1:
            result["options"] = "Sensor fault flag"

        # Dispatch on the message type
        if msg_type == 0x01:
            result.update(decode_temp_rh_data(decoded))
        elif msg_type == 0x07:
            result.update(decode_fw_version(decoded))
        elif msg_type == 0x0A:
            result.update(decode_battery_voltage(decoded))
        elif msg_type == 0x0B:
            result.update(decode_rtd_data(decoded))
        else:
            raise Exception(f"Message type {msg_type} not implemented")

        if DEBUG_OUTPUT:
            print(f"Output: {json.dumps(result, indent=2)}")

        return result


def decode_temp_rh_data(decoded):
    # Dict for result
    result = {}

    # Message type
    result["msg_type"] = "SendTempRHData"

    # Fractional portion of humidity measurement in %
    humidity_fract = decoded[2]
    # Integer portion of humidity measurement in %
    humidity_int = decoded[3]
    # Each byte needs to be decoded separately then the fractional data divided by 100.
    # The sum of the two gives the resultant value.
    humidity = humidity_int + (humidity_fract / 100)
    result["humidity"] = humidity

    # Fractional portion of temperature measurement in C
    temp_fract = helpers.bin8dec(decoded[4])
    # Integer portion of temperature measurement in C
    temp_int = helpers.bin8dec(decoded[5])
    # Each byte needs to be decoded separately then the fractional data divided by 100.
    # The sum of the two gives the resultant value.
    temperature = temp_int + (temp_fract / 100)
    result["temperature"] = temperature

    # Battery capacity
    batt_cap = decoded[6]

    # Index for percentage of battery capacity remaining
    if batt_cap == 0:
        result["battery_capacity"] = "0-5%"
    elif batt_cap == 1:
        result["battery_capacity"] = "5-20%"
    elif batt_cap == 2:
        result["battery_capacity"] = "20-40%"
    elif batt_cap == 3:
        result["battery_capacity"] = "40-60%"
    elif batt_cap == 4:
        result["battery_capacity"] = "60-80%"
    elif batt_cap == 5:
        result["battery_capacity"] = "80-100%"
    else:
        result["battery_capacity"] = "unsupported value"

    # Number of backlog alarm messages in sensor FLASH
    alarm_msg_cnt = decoded[7] << 8 | decoded[8]
    result["alarm_msg_count"] = alarm_msg_cnt

    # Number of backlog non-alarm messages in sensor FLASH
    backlog_msg_cnt = decoded[9] << 8 | decoded[10]
    result["backlog_msg_count"] = backlog_msg_cnt

    if DEBUG_OUTPUT:
        print(f"Output: {json.dumps(result,indent=2)}")

    return result


def decode_fw_version(decoded):
    # Dict for result
    result = {}

    # Set message type
    result["msg_type"] = "SendFWVersion"

    # Version year
    result["year"] = decoded[2]
    # Version month
    result["month"] = decoded[3]
    # Version day
    result["day"] = decoded[4]

    # Version major
    result["version_major"] = decoded[5]
    # Version minor
    result["version_minor"] = decoded[6]

    # Part number of firmware
    part_number = decoded[7] << 24 | decoded[8] << 16 | decoded[9] << 8 | decoded[10]
    result["part_number"] = helpers.bin32dec(part_number)

    if DEBUG_OUTPUT:
        print(f"Output: {json.dumps(result,indent=2)}")

    return result


def decode_battery_voltage(decoded):
    # Dict for result
    result = {}

    # Set message type
    result["msg_type"] = "SendBatteryVoltage"

    # Fractional part of the last measured battery voltage
    volt_fract = helpers.bin8dec(decoded[2])
    # Integer part of the last measured battery voltage
    volt_int = helpers.bin8dec(decoded[3])
    # Each byte needs to be decoded separately then the fractional data divided by 100.
    # The sum of the two gives the resultant value.
    volt = volt_int + (volt_fract / 100)
    result["voltage"] = volt

    if DEBUG_OUTPUT:
        print(f"Output: {json.dumps(result,indent=2)}")

    return result


def decode_rtd_data(decoded):
    # Dict for result
    result = {}

    # Message type
    result["msg_type"] = "SendRTDData"

    # Fractional portion of temperature measurement in C
    temp_fract = decoded[2] << 8 | decoded[3]
    temp_fract = helpers.bin16dec(temp_fract)
    # Integer portion of temperature measurement in C
    temp_int = decoded[4] << 8 | decoded[5]
    temp_int = helpers.bin16dec(temp_int)
    # Each bytes needs to be decoded separately then the fractional data divided by 100.
    # The sum of the two gives the resultant value.
    temperature = temp_int + (temp_fract / 100)
    result["temperature"] = temperature

    # Battery capacity
    batt_cap = decoded[6]

    # Index for percentage of  battery capacity remaining
    if batt_cap == 0:
        result["battery_capacity"] = "0-5%"
    elif batt_cap == 1:
        result["battery_capacity"] = "5-20%"
    elif batt_cap == 2:
        result["battery_capacity"] = "20-40%"
    elif batt_cap == 3:
        result["battery_capacity"] = "40-60%"
    elif batt_cap == 4:
        result["battery_capacity"] = "60-80%"
    elif batt_cap == 5:
        result["battery_capacity"] = "80-100%"
    else:
        result["battery_capacity"] = "unsupported value"

    # Number of backlog alarm messages in sensor FLASH
    alarm_msg_cnt = decoded[7] << 8 | decoded[8]
    result["alarm_msg_count"] = alarm_msg_cnt

    # Number of backlog non-alarm messages in sensor FLASH
    backlog_msg_cnt = decoded[9] << 8 | decoded[10]
    result["backlog_msg_count"] = backlog_msg_cnt

    if DEBUG_OUTPUT:
        print(f"Output: {json.dumps(result,indent=2)}")

    return result


# Tests
if __name__ == "__main__":
    test_definition = [
        {
            "input_encoding": "hex",
            "input_value": "01001E0141190200000000",
            "output": {
                "msg_type": "SendTempRHData",
                "options": "Undefined",
                "humidity": 1.3,
                "temperature": 25.65,
                "battery_capacity": "20-40%",
                "alarm_msg_count": 0,
                "backlog_msg_count": 0
            }
        },
        {
            "input_encoding": "base64",
            "input_value": "BwkUAxoGAABJPnI=",
            "output": {
                "msg_type": "SendFWVersion",
                "options": "Sensor reset flag",
                "year": 20,
                "month": 3,
                "day": 26,
                "version_major": 6,
                "version_minor": 0,
                "part_number": 4800114
            }
        },
        {
            "input_encoding": "hex",
            "input_value": "0A000A03",
            "output": {
                "msg_type": "SendBatteryVoltage",
                "options": "Undefined",
                "voltage": 3.1
            }
        },
        {
            "input_encoding": "hex",
            "input_value": "0A010A03",
            "output": {
                "msg_type": "SendBatteryVoltage",
                "options": "Sensor request for server time",
                "voltage": 3.1
            }
        },
        {
            "input_encoding": "base64",
            "input_value": "CxEAAAAABAAAAAA=",
            "output": {
                "msg_type": "SendRTDData",
                "options": "Sensor fault flag",
                "temperature": 0.0,
                "battery_capacity": "60-80%",
                "alarm_msg_count": 0,
                "backlog_msg_count": 0
            }
        },
        {
            "input_encoding": "hex",
            "input_value": "07 00 00 01 01 00 00 00 49 3E 6F",
            "output": {
                "msg_type": "SendFWVersion",
                "options": "Undefined",
                "year": 0,
                "month": 1,
                "day": 1,
                "version_major": 0,
                "version_minor": 0,
                "part_number": 4800111
            }
        },
        {
            "input_encoding": "hex",
            "input_value": "0B 01 00 00 00 10 02 00 00 00 00",
            "output": {
                "msg_type": "SendRTDData",
                "options": "Sensor request for server time",
                "temperature": 16.0,
                "battery_capacity": "20-40%",
                "alarm_msg_count": 0,
                "backlog_msg_count": 0
            }
        },
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
                    f'"{testcase.get("input_value")}" : Successful test for key "{key}", value "{testcase.get("output").get(key)}"')
