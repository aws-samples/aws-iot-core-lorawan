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
# https://www.adeunis.com/wp-content/uploads/2020/04/FTD2.zip

import base64
import json

import helpers

# DEBUG MODE
DEBUG_OUTPUT = False


#   | byte |  bit7  |  bit6  | bit5 | bit4 | bit3 | bit2 | bit1 | bit0 |
#   |------|--------|--------|------|------|------|------|------|------|
#   |   0  |   Status                                                  |
#   |------|-----------------------------------------------------------|
#   |   1  |   Temperature                                             |
#   |------|-----------------------------------------------------------|
#   |   2  |   GPS Latitude                                            |
#   |   3  |                                                           |
#   |   4  |                                                           |
#   |   5  |                                                           |
#   |------|-----------------------------------------------------------|
#   |   6  |   GPS Longitude                                           |
#   |   7  |                                                           |
#   |   8  |                                                           |
#   |   9  |                                                           |
#   |------|-----------------------------------------------------------|
#   |  10  |   GPS Quality                                             |
#   |------|-----------------------------------------------------------|
#   |  11  |   UL Counter                                              |
#   |------|-----------------------------------------------------------|
#   |  12  |   DL Counter                                              |
#   |------|-----------------------------------------------------------|
#   |  13  |   Battery level                                           |
#   |  14  |                                                           |
#   |------|-----------------------------------------------------------|
#   |  15  |   RSSI                                                    |
#   |------|-----------------------------------------------------------|
#   |  16  |   SNR                                                     |


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

    # The first byte shows the presence of information that is contained in the payload
    # Byte 1 - Status
    # True = Data is present in the payload
    # False = Data is missing from the Payload
    if len(decoded):
        # getting the first byte
        status_presence = decoded[byte_index]
        status_presence_rssi_snr = status_presence & 0b00000001
        if status_presence_rssi_snr == 0b1:
            status_presence_rssi_snr = True
        elif status_presence_rssi_snr == 0b0:
            status_presence_rssi_snr = False

        status_presence_battery_lvl = (status_presence & 0b00000010) >> 1
        if status_presence_battery_lvl == 0b1:
            status_presence_battery_lvl = True
        elif status_presence_battery_lvl == 0b0:
            status_presence_battery_lvl = False

        status_presence_downlink = (status_presence & 0b00000100) >> 2
        if status_presence_downlink == 0b1:
            status_presence_downlink = True
        elif status_presence_downlink == 0b0:
            status_presence_downlink = False

        status_presence_uplink = (status_presence & 0b00001000) >> 3
        if status_presence_uplink == 0b1:
            status_presence_uplink = True
        elif status_presence_uplink == 0b0:
            status_presence_uplink = False

        status_presence_gps = (status_presence & 0b00010000) >> 4
        if status_presence_gps == 0b1:
            status_presence_gps = True
        elif status_presence_gps == 0b0:
            status_presence_gps = False

        status_presence_trigger_button = (status_presence & 0b00100000) >> 5
        if status_presence_trigger_button == 0b001:
            status_presence_trigger_button = True
        elif status_presence_trigger_button == 0b000:
            status_presence_trigger_button = False

        status_presence_trigger_acc = (status_presence & 0b01000000) >> 6
        if status_presence_trigger_acc == 0b1:
            status_presence_trigger_acc = True
        elif status_presence_trigger_acc == 0b0:
            status_presence_trigger_acc = False

        status_presence_temp = (status_presence & 0b10000000) >> 7
        if status_presence_temp == 0b1:
            status_presence_temp = True
        elif status_presence_temp == 0b0:
            status_presence_temp = False

        # adding the trigger action to the result
        if status_presence_trigger_button:
            result["trigger"] = "Button"
        elif status_presence_trigger_acc:
            result["trigger"] = "Accelerometer"

        byte_index += 1

        # Temperature - one Byte
        if status_presence_temp and len(decoded) >= byte_index + 1:
            result["temperature"] = helpers.bin8dec(decoded[byte_index])
            byte_index += 1

        # Latitude - 4 Bytes
        if status_presence_gps and len(decoded) >= byte_index + 9:
            lat_bcd_deg_tenth = (decoded[byte_index] & 0b11110000) >> 4
            lat_bcd_deg_whole = decoded[byte_index] & 0b00001111
            byte_index += 1
            lat_bcd_min_tenth = (decoded[byte_index] & 0b11110000) >> 4
            lat_bcd_min_whole = decoded[byte_index] & 0b00001111
            byte_index += 1
            lat_bcd_dec_tenth = (decoded[byte_index] & 0b11110000) >> 4
            lat_bcd_dec_hundredth = decoded[byte_index] & 0b00001111
            byte_index += 1
            lat_bcd_dec_thousandth = (decoded[byte_index] & 0b11110000) >> 4
            # lat_not_used = decoded[byte_index] & 0b00001110

            # when the bit on the position 0 is 1 variable gets the value -1 else 1
            lat_hemisphere = decoded[byte_index] & 0b00000001
            if lat_hemisphere == 0b1:
                lat_hemisphere = -1
            elif lat_hemisphere == 0b0:
                lat_hemisphere = 1

            # format the latitude values in Decimal Degrees
            result["latitude"] = lat_hemisphere * (
                    lat_bcd_deg_tenth * 10 + lat_bcd_deg_whole + (
                     lat_bcd_min_tenth * 10 + lat_bcd_min_whole + lat_bcd_dec_tenth * 0.1 + lat_bcd_dec_hundredth * 0.01
                     + lat_bcd_dec_thousandth * 0.001) / 60)

            byte_index += 1

            # Longitude - four Bytes
            long_bcd_deg_hundredth = (decoded[byte_index] & 0b11110000) >> 4
            long_bcd_deg_tenth = decoded[byte_index] & 0b00001111
            byte_index += 1
            long_bcd_deg_whole = (decoded[byte_index] & 0b11110000) >> 4
            long_bcd_min_tenth = decoded[byte_index] & 0b00001111
            byte_index += 1
            long_bcd_min_whole = (decoded[byte_index] & 0b11110000) >> 4
            long_bcd_dec_tenth = decoded[byte_index] & 0b00001111
            byte_index += 1
            long_bcd_dec_hundredth = (decoded[byte_index] & 0b11110000) >> 4
            # long_not_used = decoded[byte_index] & 0b00001110

            # when the bit on the position 0 is 1 variable gets the value -1 else 1
            long_hemisphere = decoded[byte_index] & 0b00000001
            if long_hemisphere == 0b1:
                long_hemisphere = -1
            elif long_hemisphere == 0b0:
                long_hemisphere = 1

            # format the latitude values in Decimal Degrees
            result["longitude"] = long_hemisphere * (
                    long_bcd_deg_hundredth * 100 + long_bcd_deg_tenth * 10 + long_bcd_deg_whole + (
                     long_bcd_min_tenth * 10 + long_bcd_min_whole + long_bcd_dec_tenth * 0.1 + long_bcd_dec_hundredth *
                     0.01) / 60)

            byte_index += 1

            # GPS quality - one Byte
            result["gps_quality"] = {
                "reception_scale": "Unknown",
                "number_satellites": decoded[byte_index] & 0b00001111
            }
            reception_scale = (decoded[byte_index] & 0b11110000) >> 4
            if reception_scale == 1:
                result["gps_quality"]["reception_scale"] = "Good"
            elif reception_scale == 2:
                result["gps_quality"]["reception_scale"] = "Average"
            elif reception_scale == 3:
                result["gps_quality"]["reception_scale"] = "Poor"

            byte_index += 1

        # Uplink counter - one Byte
        if status_presence_uplink and len(decoded) >= byte_index + 1:
            result["uplink_frame_counter"] = decoded[byte_index]
            byte_index += 1

        # Downlink counter - one Byte
        if status_presence_downlink and len(decoded) >= byte_index + 1:
            result["downlink_frame_counter"] = decoded[byte_index]
            byte_index += 1

        # Battery level - two Bytes
        if status_presence_battery_lvl and len(decoded) >= byte_index + 2:
            result["battery_lvl"] = ((decoded[byte_index] << 8) | decoded[byte_index + 1])
            byte_index += 2

        # RSSI - one Byte
        # SNR - one Byte
        if status_presence_rssi_snr and len(decoded) >= byte_index + 2:
            result["rssi/snr"] = {
                "rssi_dbm": decoded[byte_index],
                "snr_db": helpers.bin8dec(decoded[byte_index + 1])
            }

        if DEBUG_OUTPUT:
            print(f"Output: {json.dumps(result, indent=2)}")

        return result


# Tests
if __name__ == "__main__":
    test_definition = [
        {
            "input_encoding": "hex",
            "input_value": "BF1B45159690005345002720200FC95207",
            "output": {
                "temperature": 27,
                "trigger": "Button",
                "latitude": 45.26615,
                "longitude": 005.575,
                "gps_quality": {
                    "reception_scale": "Average",
                    "number_satellites": 7
                },
                "uplink_frame_counter": 32,
                "downlink_frame_counter": 32,
                "battery_lvl": 4041,
                "rssi/snr": {
                    "rssi_dbm": 82,
                    "snr_db": 7
                }
            }
        },
        {
            "input_encoding": "hex",
            "input_value": "3F45159690005345002720200FC95207",
            "output": {
                "trigger": "Button",
                "latitude": 45.26615,
                "longitude": 005.575,
                "gps_quality": {
                    "reception_scale": "Average",
                    "number_satellites": 7
                },
                "uplink_frame_counter": 32,
                "downlink_frame_counter": 32,
                "battery_lvl": 4041,
                "rssi/snr": {
                    "rssi_dbm": 82,
                    "snr_db": 7
                }
            }
        },
        {
            "input_encoding": "hex",
            "input_value": "AF1B20200FC95207",
            "output": {
                "temperature": 27,
                "trigger": "Button",
                "uplink_frame_counter": 32,
                "downlink_frame_counter": 32,
                "battery_lvl": 4041,
                "rssi/snr": {
                    "rssi_dbm": 82,
                    "snr_db": 7
                }
            }
        },
        {
            "input_encoding": "hex",
            "input_value": "DFB035159690004345001F0F0D1B589CBB",
            "output": {
                "temperature": -80,
                "trigger": "Accelerometer",
                "latitude": 35.26615,
                "longitude": 004.575,
                "gps_quality": {
                    "reception_scale": "Good",
                    "number_satellites": 15
                },
                "uplink_frame_counter": 15,
                "downlink_frame_counter": 13,
                "battery_lvl": 7000,
                "rssi/snr": {
                    "rssi_dbm": 156,
                    "snr_db": -69
                }
            }
        },
        {
            "input_encoding": "hex",
            "input_value": "D7B035159690004345001F0D1B589CBB",
            "output": {
                "temperature": -80,
                "trigger": "Accelerometer",
                "latitude": 35.26615,
                "longitude": 004.575,
                "gps_quality": {
                    "reception_scale": "Good",
                    "number_satellites": 15
                },
                "downlink_frame_counter": 13,
                "battery_lvl": 7000,
                "rssi/snr": {
                    "rssi_dbm": 156,
                    "snr_db": -69
                }
            }
        },
        {
            "input_encoding": "hex",
            "input_value": "D3B035159690004345001F1B589CBB",
            "output": {
                "temperature": -80,
                "trigger": "Accelerometer",
                "latitude": 35.26615,
                "longitude": 004.575,
                "gps_quality": {
                    "reception_scale": "Good",
                    "number_satellites": 15
                },
                "battery_lvl": 7000,
                "rssi/snr": {
                    "rssi_dbm": 156,
                    "snr_db": -69
                }
            }
        },
        {
            "input_encoding": "hex",
            "input_value": "D1B035159690004345001F9CBB",
            "output": {
                "temperature": -80,
                "trigger": "Accelerometer",
                "latitude": 35.26615,
                "longitude": 004.575,
                "gps_quality": {
                    "reception_scale": "Good",
                    "number_satellites": 15
                },
                "rssi/snr": {
                    "rssi_dbm": 156,
                    "snr_db": -69
                }
            }
        },
        {
            "input_encoding": "hex",
            "input_value": "80b0",
            "output": {
                "temperature": -80,
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
