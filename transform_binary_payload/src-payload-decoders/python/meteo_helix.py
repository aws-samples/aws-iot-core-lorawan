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
# https://www.baranidesign.com/meteohelix-message-decoder

import base64

# DEBUG MODE
DEBUG_OUTPUT = False


#   Send Temp RH Data Notification
#   | byte |  bit7  |  bit6  | bit5 | bit4 | bit3 | bit2 | bit1 | bit0 |
#   |------|--------|--------|------|------|------|------|------|------|
#   |   0  | Temp.  | Battery                            | MsgType     |
#   |------|-----------------------------------------------------------|
#   |   1  |   Temperature                                             |
#   |------|-----------------------------------------------------------|
#   |   2  |   T-min                                     | Temperature |
#   |------|-----------------------------------------------------------|
#   |   3  |   Humidity      |              T_max                      |
#   |------|-----------------------------------------------------------|
#   |   4  |Pressure|              Humidity                            |
#   |------|-----------------------------------------------------------|
#   |   5  |   Pressure                                                |
#   |------|-----------------------------------------------------------|
#   |   6  |   Irradiation          |       Pressure                   |
#   |------|-----------------------------------------------------------|
#   |   7  | Irr_max|        Irradiation                               |
#   |   8  |   Irr_max                                                 |
#   |------|-----------------------------------------------------------|
#   |   9  |  Rain(revolving counter)                                  |
#   |  10  |  Min_time_between_rain_gauge_clicks                       |


# from python byteobject to string
def data_to_bits(data):
    binary = ""
    for byte in data:
        byte_raw = '0000000' + str(bin(byte)[2:])
        byte_pad = byte_raw[-8:]
        binary += byte_pad
    return binary


# bit shifting
def bit_shift(binary, start_bit_offset, bits):
    end_bit_offset = start_bit_offset + bits
    num = int(binary[start_bit_offset:end_bit_offset], 2)
    start_bit_offset += bits
    return start_bit_offset, num


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
        binary = data_to_bits(decoded)
        # if physical property is 1111... =  Sensor Error
        if "0" not in binary:
            return {"Error": "Sensor Error or N/A"}

        # Message type - 2 bits
        start_bit_offset, msg_type = bit_shift(binary, 0, 2)

        # Battery - 5 bits
        start_bit_offset, batt = bit_shift(binary, start_bit_offset, 5)
        batt = round(batt * 0.05 + 3, 2)

        # Temperature - 11 bits
        start_bit_offset, temp = bit_shift(binary, start_bit_offset, 11)
        temp = round(temp * 0.1 - 100, 2)

        # T_min - 6 bits
        start_bit_offset, t_min = bit_shift(binary, start_bit_offset, 6)
        t_min = round((temp - t_min * 0.1), 2)

        # T_max - 6 bits
        start_bit_offset, t_max = bit_shift(binary, start_bit_offset, 6)
        t_max = round((temp + t_max * 0.1), 2)

        # Humidity - 9 bits
        start_bit_offset, humid = bit_shift(binary, start_bit_offset, 9)
        humid = round(humid * 0.2, 2)

        # Pressure - 14 bits
        start_bit_offset, press = bit_shift(binary, start_bit_offset, 14)
        press = press * 5 + 50000

        # Irradiation - 10 bits
        start_bit_offset, irrad = bit_shift(binary, start_bit_offset, 10)
        irrad = irrad * 2

        # Irr_max - 9 bits
        start_bit_offset, irr_max = bit_shift(binary, start_bit_offset, 9)
        irr_max = irrad + (irr_max * 2)

        # Rain - 8 bits
        start_bit_offset, rain = bit_shift(binary, start_bit_offset, 8)
        rain = round(rain, 2)

        # Min_time_between_rain_gauge_clicks - 8 bits
        start_bit_offset, min_time_between = bit_shift(binary, start_bit_offset, 8)

        result = {
            "Type": msg_type,
            "Battery": batt,
            "Temperature": temp,
            "T_min": t_min,
            "T_max": t_max,
            "Humidity": humid,
            "Pressure": press,
            "Irradiation": irrad,
            "Irr_max": irr_max,
            "Rain": rain,
            "Rain_min_time": min_time_between
        }
        return result


# Tests
if __name__ == "__main__":
    test_definition = [
        {
            "input_encoding": "hex",
            "input_value": "712723674fa31afad303f0",
            "output": {
                "Type": 1,
                "Battery": 4.2,
                "Temperature": 18,
                "T_min": 14.5,
                "T_max": 20.5,
                "Humidity": 84.60,
                "Pressure": 117055,
                "Irradiation": 762,
                "Irr_max": 1184,
                "Rain": 3,
                "Rain_min_time": 240
            }
        },
        {
            "input_encoding": "hex",
            "input_value": "FFFFFFFFFFFFFFFFFFFFFFFF",
            "output": {"Error": "Sensor Error or N/A"}
        },
        {
            "input_encoding": "hex",
            "input_value": "7fab34785fb42bfbf404f000",
            "output": {
                "Type": 1,
                "Battery": 4.55,
                "Temperature": 70.8,
                "T_min": 65.6,
                "T_max": 73.8,
                "Humidity": 9.4,
                "Pressure": 119785,
                "Irradiation": 1018,
                "Irr_max": 2018,
                "Rain": 4,
                "Rain_min_time": 240
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
