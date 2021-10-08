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


def dict_from_payload(base64_input: str):

    payload_bytes = base64.b64decode(base64_input)

    if payload_bytes[0] == 0x00:
            result = {
                "messagetype": "switchstatus",
                "switch_status": "off"
            }
    elif payload_bytes[0] == 0x01:
            result = {
                "messagetype": "switchstatus",
                "switch_status": "off"
            }
    elif payload_bytes[0] == 0xF0:
            result = {
                "messagetype": "interval",
                "interval": payload_bytes[2] | payload_bytes[1] << 8
            }
    

    return result


# Tests
if __name__ == "__main__":
    test_definition = [
        {
            "input": "00",
            "output": {
                "switch_status": "off"
            }
        },
        {
            "input": "01",
            "output": {
                "switch_status": "on"
            }
        },
        {
            "input": "F0",
            "output": {
                "switch_status": "on"
            }
        }
    ]

    for test in test_definition:
        base64_input = base64.b64encode(
            bytearray.fromhex(test.get("input"))).decode("utf-8")
        output = dict_from_payload(base64_input)
        for key in test.get("output"):
            if(test.get("output").get(key) != output.get(key)):
                raise Exception(
                    f'Assertion failed for input {test.get("input")}, key {key}, expected {test.get("output").get(key)}, got {output.get(key)} ')
            else:
                print("OK")
