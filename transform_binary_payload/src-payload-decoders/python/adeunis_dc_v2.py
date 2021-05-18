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
# https://www.adeunis.com/wp-content/uploads/2019/09/DRYCONTACTS_V2-Technical_Reference_Manual_APP_2.1-02.02.2021.pdf

import base64

# DEBUG MODE
DEBUG_OUTPUT = False


#    Data frame (0x40)
#   | byte |  bit7  |  bit6  | bit5 | bit4 | bit3 | bit2 | bit1 | bit0 |
#   |------|--------|--------|------|------|------|------|------|------|
#   |   0  |   Frame code                                              |
#   |------|-----------------------------------------------------------|
#   |   1  |   Status                                                  |
#   |------|-----------------------------------------------------------|
#   |   2  |   Channel 1 info                                          |
#   |   3  |                                                           |
#   |------|-----------------------------------------------------------|
#   |   4  |   Channel 2 info                                          |
#   |   5  |                                                           |
#   |------|-----------------------------------------------------------|
#   |   6  |   Channel 3 info                                          |
#   |   7  |                                                           |
#   |------|-----------------------------------------------------------|
#   |   8  |   Channel 4 info                                          |
#   |   9  |                                                           |
#   |------|-----------------------------------------------------------|
#   |  10  |   Details                                                 |
#   |------|-----------------------------------------------------------|
#   |  11  |   Timestamp                                               |
#   |  12  |                                                           |
#   |  13  |                                                           |
#   |  14  |                                                           |

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
    # Payload
    # The size of the payload varies depending on the information that is send.
    decoded = base64.b64decode(base64_input)
    # Index for iterating over the payload bytes
    byte_index = 0
    # result dictionary
    result = {}

    # Printing the debug output
    if DEBUG_OUTPUT:
        print(f"Input: {decoded.hex().upper()}")

    # The first byte shows the Frame code
    # Byte 1 - Frame code
    # 0x10 Product configuration, 0x20 Network configuration, 0x2F Set state or pulse ACK, 0x30 Keep alive frame
    # 0x40 Data frame, 0x59 Time counting frame, 0x31 Response to Get register request,
    # 0x33 Response to Set register request
    if len(decoded):
        # getting the first byte
        frame_code = decoded[0]

        # getting the frame type
        if frame_code == 0x10:
            result["type"] = "0x10 Dry Contacts 2 configuration"
        elif frame_code == 0x20:
            result["type"] = "0x20 Configuration"
        elif frame_code == 0x2F:
            result["type"] = "0x2f Downlink ack"
        elif frame_code == 0x30:
            result["type"] = "0x30 Dry Contacts 2 keep alive"
        elif frame_code == 0x33:
            result["type"] = "0x33 Set register status"
        elif frame_code == 0x40:
            result["type"] = "0x40 Dry Contacts 2 data"
        elif frame_code == 0x59:
            result["type"] = "0x59 Dry Contacts 2 time counting data"
        else:
            result["type"] = "Invalid frame code"

        # Status - one Byte
        status = decoded[1]

        # bit0 - Configuration Done
        config = status & 0b00000001
        if config & 0b1:
            config = True
        else:
            config = False

        # bit1 - Low Battery
        low_bat = (status & 0b00000010) >> 1
        if low_bat & 0b1:
            low_bat = True
        else:
            low_bat = False

        # bit2 - Timestamp
        timestamp = (status & 0b00000100) >> 2
        if timestamp & 0b1:
            timestamp = True
        else:
            timestamp = False

        # bit3 - AppFlag1
        app_flag_1 = (status & 0b00001000) >> 3
        if app_flag_1 & 0b1:
            app_flag_1 = True
        else:
            app_flag_1 = False

        # bit4 - AppFlag2
        app_flag_2 = (status & 0b00010000) >> 4
        if app_flag_2 & 0b1:
            app_flag_2 = True
        else:
            app_flag_2 = False

        # bit5-6 - Frame Counter
        frame_counter = (status & 0b11100000) >> 5

        # check if there is no error
        no_error = not (config or low_bat or timestamp or app_flag_1 or app_flag_2)

        # building the result
        result["status"] = {
            "frameCounter": frame_counter,
            "noError": no_error,
            "lowBattery": low_bat,
            "configurationDone": config,
            "timestamp": timestamp
        }

        if frame_code == 0x40:
            # channel a - byte 2&3
            channel_a = ((decoded[2] << 8) | decoded[3])
            result["channelA"] = {
                "value": channel_a
            }

            # channel b - byte 4&5
            channel_b = ((decoded[4] << 8) | decoded[5])
            result["channelB"] = {
                "value": channel_b
            }

            # channel c - byte 6&7
            channel_c = ((decoded[6] << 8) | decoded[7])
            result["channelC"] = {
                "value": channel_c
            }

            # channel d - byte 8&9
            channel_d = ((decoded[8] << 8) | decoded[9])
            result["channelD"] = {
                "value": channel_d
            }

            # details - byte 10
            # Define precisely the input/output state
            details = decoded[10]

            # channel a
            channel_a_current_state = details & 0b00000001
            if channel_a_current_state & 0b1:
                result["channelA"]["currentState"] = True
            else:
                result["channelA"]["currentState"] = False

            channel_a_previous_frame = (details & 0b00000010) >> 1
            if channel_a_previous_frame & 0b1:
                result["channelA"]["previousFrameState"] = True
            else:
                result["channelA"]["previousFrameState"] = False

            # channel b
            channel_b_current_state = (details & 0b00000100) >> 2
            if channel_b_current_state & 0b1:
                result["channelB"]["currentState"] = True
            else:
                result["channelB"]["currentState"] = False

            channel_b_previous_frame = (details & 0b00001000) >> 3
            if channel_b_previous_frame & 0b1:
                result["channelB"]["previousFrameState"] = True
            else:
                result["channelB"]["previousFrameState"] = False

            # channel c
            channel_c_current_state = (details & 0b00010000) >> 4
            if channel_c_current_state & 0b1:
                result["channelC"]["currentState"] = True
            else:
                result["channelC"]["currentState"] = False

            channel_c_previous_frame = (details & 0b00100000) >> 5
            if channel_c_previous_frame & 0b1:
                result["channelC"]["previousFrameState"] = True
            else:
                result["channelC"]["previousFrameState"] = False

            # channel d
            channel_d_current_state = (details & 0b01000000) >> 6
            if channel_d_current_state & 0b1:
                result["channelD"]["currentState"] = True
            else:
                result["channelD"]["currentState"] = False

            channel_d_previous_frame = (details & 0b10000000) >> 7
            if channel_d_previous_frame & 0b1:
                result["channelD"]["previousFrameState"] = True
            else:
                result["channelD"]["previousFrameState"] = False

            # timestamp in EPOCH 2013
            if timestamp and len(decoded) > 10:
                timestamp_data = ((decoded[11] << 24) | decoded[12] << 16 | decoded[13] << 8 | decoded[14])
                result["timestamp"] = timestamp_data

        return result


# Tests
if __name__ == "__main__":
    test_definition = [
        {
            "input_encoding": "base64",
            "input_value": "QMAAAQACAAMABKU=",
            "output": {
                "type": "0x40 Dry Contacts 2 data",
                "status": {
                    "frameCounter": 6,
                    "noError": True,
                    "lowBattery": False,
                    "configurationDone": False,
                    "timestamp": False
                },
                "channelA": {
                    "value": 1,
                    "currentState": True,
                    "previousFrameState": False
                },
                "channelB": {
                    "value": 2,
                    "currentState": True,
                    "previousFrameState": False
                },
                "channelC": {
                    "value": 3,
                    "currentState": False,
                    "previousFrameState": True
                },
                "channelD": {
                    "value": 4,
                    "currentState": False,
                    "previousFrameState": True
                }
            }
        },
        {
            "input_encoding": "hex",
            "input_value": "4040000101000000000146",
            "output": {
                "type": "0x40 Dry Contacts 2 data",
                "status": {
                    "frameCounter": 2,
                    "noError": True,
                    "lowBattery": False,
                    "configurationDone": False,
                    "timestamp": False
                },
                "channelA": {
                    "value": 1,
                    "currentState": False,
                    "previousFrameState": True
                },
                "channelB": {
                    "value": 256,
                    "currentState": True,
                    "previousFrameState": False
                },
                "channelC": {
                    "value": 0,
                    "currentState": False,
                    "previousFrameState": False
                },
                "channelD": {
                    "value": 1,
                    "currentState": True,
                    "previousFrameState": False
                }
            }
        },
        {
            "input_encoding": "hex",
            "input_value": "40AB00F10002000100009C",
            "output": {
                "type": "0x40 Dry Contacts 2 data",
                "status": {
                    "frameCounter": 5,
                    "noError": False,
                    "lowBattery": True,
                    "configurationDone": True,
                    "timestamp": False
                },
                "channelA": {
                    "value": 241,
                    "currentState": False,
                    "previousFrameState": False
                },
                "channelB": {
                    "value": 2,
                    "currentState": True,
                    "previousFrameState": True
                },
                "channelC": {
                    "value": 1,
                    "currentState": True,
                    "previousFrameState": False
                },
                "channelD": {
                    "value": 0,
                    "currentState": False,
                    "previousFrameState": True
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
            if testcase.get("output").get(key) != output.get(key):
                raise Exception(
                    f'Assertion failed for input {testcase.get("input_value")}, key {key}, expected {testcase.get("output").get(key)}, got {output.get(key)}')
            else:
                print(
                    f'"{testcase.get("input_value")}" : Successful test for key "{key}", value "{testcase.get("output").get(key)}"')
