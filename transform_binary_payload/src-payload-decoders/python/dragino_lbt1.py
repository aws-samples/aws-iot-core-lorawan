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
import json
import logging

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def convert_bytes_to_uint(input):
    print(f"c input is {input} of len {len(input)}")
    result = 0
    for i in range(0, len(input)):
        factor = (i+1) ** 8
        print(
            f"input[{i}] is {input[i]}, 0x{hex(input[i])}, factor is {factor}")
        result += input[i]*factor
    return result


def to_ascii(input):
    bytes_object = bytes.fromhex(input)
    ascii_string = bytes_object.decode("ASCII")
    return ascii_string


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
    logger.debug(f"Input hex is {decoded.hex()}")

    battery_value = ((decoded[0] << 8 | decoded[1])) / 1000
    step_count = ((decoded[2] & 0x0F) << 16) | (decoded[3] << 8) | (decoded[4])
    mode = decoded[5]

    uuid = 0
    if mode == 3:
        uuid = decoded[6:18]
        major = decoded[18:22]
        minor = decoded[22:26]
        power = decoded[26:28]
        rssi = decoded[28:32]

        result = {
            "battery_value": battery_value,
            "step_count": step_count,
            "mode": mode,
            "uuid": uuid.decode(),
            "major": int(to_ascii(major.hex()), 16),
            "minor": int(to_ascii(minor.hex()), 16),
            "power": int(to_ascii(power.hex()), 16)-256,
            "rssi": int(to_ascii(rssi.hex()), 16)
        }
    elif mode == 2:
        uuid = decoded[6:6+32]
        addr = decoded[38:39+12]
        result = {
            "battery_value": battery_value,
            "step_count": step_count,
            "mode": mode,
            "uuid": uuid.decode(),
            "addr": addr.decode()
        }
    elif mode == 1:
        uuid = decoded[6:11]
        result = {
            "battery_value": battery_value,
            "step_count": step_count,
            "mode": mode,
            "uuid": uuid.decode(),
        }
    else:
        result = {
            "battery_value": battery_value,
            "step_count": step_count,
            "mode": mode,
        }

    return result


# Tests
if __name__ == "__main__":
    test_definition = [
        {

            "input_value": "DyAAAAACMDExMjIzMzQ0NTU2Njc3ODg5OUFBQkJDQ0RERUVGRjBFREYwOUM1QjVCNDc=",
            "input_encoding": "base64",
            "output": {"battery_value": 3.872, "step_count": 0, "mode": 2, "uuid": "0112233445566778899AABBCCDDEEFF0", "addr": "DF09C5B5B47"}
        },
        {

            "input_value": "DxwAAAIDQUJCQ0NEREVFRkYwMjcxMjFGNkFDMy0wNTk=",
            "input_encoding": "base64",
            "output": {"battery_value": 3.868, "step_count": 2, "mode": 3, "uuid": "ABBCCDDEEFF0", "major": 10002, "minor": 8042, "power": -61, "rssi": -89}
        },
        {

            "input_value": "DxQAAAABRUVGRjA=",
            "input_encoding": "base64",
            "output": {"battery_value": 3.86, "step_count": 0, "mode": 1, "uuid": "EEFF0"}
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
            if(testcase.get("output").get(key) != output.get(key)):
                raise Exception(
                    f'Assertion failed for input {testcase.get("input_value")}, key {key}, expected {testcase.get("output").get(key)}, got {output.get(key)}')
            else:
                print(
                    f'"{testcase.get("input_value")}" : Successfull test for key "{key}", value "{testcase.get("output").get(key)}"')
