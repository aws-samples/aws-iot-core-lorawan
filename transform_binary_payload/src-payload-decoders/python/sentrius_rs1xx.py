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
#   |   0  |   MsgType - uint8_t                                       |
#   |------|-----------------------------------------------------------|
#   |   1  |   Options - bitfield                                      |
#   |------|-----------------------------------------------------------|
#   |   2  |   Humidity Fractional - uint8_t                           |
#   |------|-----------------------------------------------------------|
#   |   3  |   Humidity Integer - uint8_t                              |
#   |------|-----------------------------------------------------------|
#   |   4  |   Temp Fractional - int8_t                                |
#   |------|-----------------------------------------------------------|
#   |   5  |   Temp Integer - int8_t                                   |
#   |------|-----------------------------------------------------------|
#   |   6  |   Battery Capacity - uint8_t                              |
#   |------|-----------------------------------------------------------|
#   |   7  |   AlarmMsg Count - uint16_t                               |
#   |   8  |                                                           |
#   |------|-----------------------------------------------------------|
#   |   9  |   BacklogMsg Count - uint8_t                              |
#   |  10  |                                                           |

#   Send FW Version Notification
#   | byte |  bit7  |  bit6  | bit5 | bit4 | bit3 | bit2 | bit1 | bit0 |
#   |------|--------|--------|------|------|------|------|------|------|
#   |   0  |   MsgType - uint8_t                                       |
#   |------|-----------------------------------------------------------|
#   |   1  |   Options - bitfield                                      |
#   |------|-----------------------------------------------------------|
#   |   2  |   Year - 0x00                                             |
#   |------|-----------------------------------------------------------|
#   |   3  |   Month - 0x00                                            |
#   |------|-----------------------------------------------------------|
#   |   4  |   Day - 0x00                                              |
#   |------|-----------------------------------------------------------|
#   |   5  |   Version Major - 0x00                                    |
#   |------|-----------------------------------------------------------|
#   |   6  |   Version Minor - 0x00                                    |
#   |------|-----------------------------------------------------------|
#   |   7  |   Part Number - uint32_t                                  |
#   |   8  |                                                           |
#   |   9  |                                                           |
#   |  10  |                                                           |

#   Send Battery Voltage
#   | byte |  bit7  |  bit6  | bit5 | bit4 | bit3 | bit2 | bit1 | bit0 |
#   |------|--------|--------|------|------|------|------|------|------|
#   |   0  |   MsgType - uint8_t                                       |
#   |------|-----------------------------------------------------------|
#   |   1  |   Options - enum                                          |
#   |------|-----------------------------------------------------------|
#   |   2  |   Voltage Fractional - int8_t                             |
#   |------|-----------------------------------------------------------|
#   |   3  |   Voltage Integer  - int8_t                               |

#   Send RTD Data Notification
#   | byte |  bit7  |  bit6  | bit5 | bit4 | bit3 | bit2 | bit1 | bit0 |
#   |------|--------|--------|------|------|------|------|------|------|
#   |   0  |   MsgType - uint8_t                                       |
#   |------|-----------------------------------------------------------|
#   |   1  |   Options - bitfield                                      |
#   |------|-----------------------------------------------------------|
#   |   2  |   Temp Fractional - int16_t                               |
#   |   3  |                                                           |
#   |------|-----------------------------------------------------------|
#   |   4  |   Temp Integer - int16_t                                  |
#   |   5  |                                                           |
#   |------|-----------------------------------------------------------|
#   |   6  |   Battery Capacity - uint8_t                              |
#   |------|-----------------------------------------------------------|
#   |   7  |   AlarmMsg Count - uint16_t                               |
#   |   8  |                                                           |
#   |------|-----------------------------------------------------------|
#   |   9  |   BacklogMsg Count - uint16_t                             |
#   |  10  |                                                           |


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

    # when payload is available
    if len(decoded):
        # Type of message
        msg_type = decoded[0]

        # Dispatch on the message type
        if msg_type == 0x01:
            result = decode_temp_rh_data(decoded)
        elif msg_type == 0x07:
            result = decode_fw_version(decoded)
        elif msg_type == 0x0A:
            result = decode_battery_voltage(decoded)
        elif msg_type == 0x0B:
            result = decode_rtd_data(decoded)
        else:
            raise Exception(f"Message type {msg_type} not implemented")

        if DEBUG_OUTPUT:
            print(f"Output: {json.dumps(result, indent=2)}")

        return result


def decode_temp_rh_data(decoded):
    # Dict for result
    result = {
        "msg_type": "SendTempRHData",
        "options": opt_sens2serv(decoded[1]),
        "humidity": helpers.bytes_to_float(decoded, 2, 2),
        "temperature": helpers.bytes_to_float(decoded, 4, 2),
        "battery_capacity": battery_capacity(decoded[6]),
        "alarm_msg_count": decoded[7] << 8 | decoded[8],  # Number of backlog alarm messages in sensor FLASH
        "backlog_msg_count": decoded[9] << 8 | decoded[10]  # Number of backlog non-alarm messages in sensor FLASH
    }

    if DEBUG_OUTPUT:
        print(f"Output: {json.dumps(result, indent=2)}")

    return result


def decode_fw_version(decoded):
    # Dict for result
    result = {
        "msg_type": "SendFWVersion",
        "options": opt_sens2serv(decoded[1]),
        "year": decoded[2],
        "month": decoded[3],
        "day": decoded[4],
        "version_major": decoded[5],
        "version_minor": decoded[6],
        "part_number": decoded[7] << 24 | decoded[8] << 16 | decoded[9] << 8 | decoded[10]
    }

    if DEBUG_OUTPUT:
        print(f"Output: {json.dumps(result, indent=2)}")

    return result


def decode_battery_voltage(decoded):
    # Dict for result
    result = {
        "msg_type": "SendBatteryVoltage",
        "options": opt_sens2serv(decoded[1]),
        "voltage": helpers.bytes_to_float(decoded, 2, 2)
    }

    if DEBUG_OUTPUT:
        print(f"Output: {json.dumps(result, indent=2)}")

    return result


# SendRTDData
def decode_rtd_data(decoded):
    # Dict for result
    result = {
        "msg_type": "SendRTDData",
        "options": opt_sens2serv(decoded[1]),
        "temperature": helpers.bytes_to_float(decoded, 2, 4),
        "battery_capacity": battery_capacity(decoded[6]),
        "alarm_msg_count": decoded[7] << 8 | decoded[8],  # Number of backlog alarm messages in sensor FLASH
        "backlog_msg_count": decoded[9] << 8 | decoded[10]  # Number of backlog non-alarm messages in sensor FLASH
    }

    if DEBUG_OUTPUT:
        print(f"Output: {json.dumps(result, indent=2)}")

    return result


# Returns battery capacity as int
def battery_capacity(bat_byte):
    # Index for percentage of  battery capacity remaining
    if bat_byte == 0:
        return 0  # 0-5%
    elif bat_byte == 1:
        return 5  # 5-20%
    elif bat_byte == 2:
        return 20  # 20-40%
    elif bat_byte == 3:
        return 40  # 40-60%
    elif bat_byte == 4:
        return 60  # 60-80%
    elif bat_byte == 5:
        return 80  # 80-100%
    else:
        return 999  # unsupported value


# results option flag
def opt_sens2serv(opt_byte):
    if helpers.is_single_bit_set(opt_byte):
        # Sensor to server message options
        if (opt_byte & 0b00000001) == 0b1:
            return "Sensor request for server time"
        elif ((opt_byte & 0b00000010) >> 1) == 0b1:
            return "Sensor configuration error"
        elif ((opt_byte & 0b00000100) >> 2) == 0b1:
            return "Sensor alarm flag"
        elif ((opt_byte & 0b00001000) >> 3) == 0b1:
            return "Sensor reset flag"
        elif ((opt_byte & 0b00010000) >> 4) == 0b1:
            return "Sensor fault flag"
        else:
            return "Undefined option"
    else:
        return "Undefined option"


# Tests
if __name__ == "__main__":
    test_definition = [
        {
            "input_encoding": "hex",
            "input_value": "01001E0141190200000000",
            "output": {
                "msg_type": "SendTempRHData",
                "options": "Undefined option",
                "humidity": 1.3,
                "temperature": 25.65,
                "battery_capacity": 20,
                "alarm_msg_count": 0,
                "backlog_msg_count": 0
            }
        },
        {
            "input_encoding": "base64",
            "input_value": "BwkUAxoGAABJPnI=",
            "output": {
                "msg_type": "SendFWVersion",
                "options": "Undefined option",
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
                "options": "Undefined option",
                "voltage": 3.1
            }
        },
        {
            "input_encoding": "base64",
            "input_value": "CxEAAAAABAAAAAA=",
            "output": {
                "msg_type": "SendRTDData",
                "options": "Undefined option",
                "temperature": 0.0,
                "battery_capacity": 60,
                "alarm_msg_count": 0,
                "backlog_msg_count": 0
            }
        },
        {
            "input_encoding": "hex",
            "input_value": "07 00 00 01 01 00 00 00 49 3E 6F",
            "output": {
                "msg_type": "SendFWVersion",
                "options": "Undefined option",
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
                "battery_capacity": 20,
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
