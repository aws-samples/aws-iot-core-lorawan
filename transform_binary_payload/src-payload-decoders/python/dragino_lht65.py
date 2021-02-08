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

    # Batter status flag
    # 00(b): Ultra Low ( BAT <= 2.50v)
    # 01(b): Low (2.50v <=BAT <= 2.55v)
    # 10(b): OK Good (2.55v <= BAT <=2.65v)
    # 11(b): Good (BAT >= 2.65v)
    battery_status_flag = (decoded[0] & 0b11000000) >> 6
    battery_status = "unknown"
    if battery_status_flag == 0b00:
        battery_status = "very low"
    elif battery_status_flag == 0b01:
        battery_status = "low"
    elif battery_status_flag == 0b10:
        battery_status = "OK"
    elif battery_status_flag == 0b11:
        battery_status = "Good"

    # Battery voltage
    battery_value = ((decoded[0] << 8 | decoded[1]) & 0x3FFF) / 1000

    # Internal sensor temperature
    if decoded[2] & 0b1000000:
        internal_temperature = ((decoded[2] << 8 | decoded[3]) - 0xFFFF)/100
    else:
        internal_temperature = (decoded[2] << 8 | decoded[3])/100

    # Humidity
    humidity = ((decoded[4] << 8 | decoded[5])/10)

    # External sensor temperature
    if decoded[7] & 0b1000000:
        external_temperature = (((decoded[7] << 8 | decoded[8]) - 0xFFFF) / 100)
    else:
        external_temperature = ((decoded[7] << 8 | decoded[8]) / 100)

    result = {
        "battery_status": battery_status,
        "battery_value": battery_value,
        "temperature_internal": internal_temperature,
        "humidity": humidity,
        "temperature_external": external_temperature,
        # "debug": {
        #     "fport": fport
        # }
    }

    return result


# Tests
if __name__ == "__main__":
    test_definition = [
        {
            "input": "CBF60B0D0376010ADD7FFF",
            "output": {
                "battery_status": "Good",
                "battery_value": 3.062,
                "temperature_internal": 28.29,
                "humidity": 88.6,
                "temperature_external": 27.81

            }
        },
        {
            "input": "CBBDF5C6022E01F54F7FFF",
            "output": {
                "battery_status": "Good",
                "battery_value": 3.005,
                "temperature_internal": -26.17,
                "humidity": 55.8,
                "temperature_external": -27.36

            }
        }
    ]

    for test in test_definition:
        base64_input = base64.b64encode(
            bytearray.fromhex(test.get("input"))).decode("utf-8")
        output = dict_from_payload(base64_input)
        for key in test.get("output"):
            if test.get("output").get(key) != output.get(key):
                raise Exception(
                    f'Assertion failed for input {test.get("input")}, key {key}, expected {test.get("output").get(key)}, got {output.get(key)} ')
