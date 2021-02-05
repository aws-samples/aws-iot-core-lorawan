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
# https://elsys.se/public/documents/Sensor_payload.pdf


import base64
import json
import helpers

DEBUG_OUTPUT = False

TYPE_RESERVED = 0x00       # Reserved
TYPE_TEMP = 0x01           #  2 bytes  Temperature          [°C]       -3276.5  -       3276.5
TYPE_RH = 0x02             #  1 byte   Humidity             [%Rh]          0    -        100
TYPE_ACC = 0x03            #  3 bytes  Acceleration X,Y,Z   [63=1G]     -127    -        127
TYPE_LIGHT = 0x04          #  2 bytes  Light                [Lux]          0    -      65535
TYPE_MOTION = 0x05         #  1 byte   Motion (PIR)         [n]            0    -        255
TYPE_CO2 = 0x06            #  2 bytes  CO2                  [ppm]          0    -      10000
TYPE_VDD = 0x07            #  2 bytes  Int battery voltage  [mV]           0    -      65535
TYPE_ANALOG1 = 0x08        #  2 bytes  Analog input 1       [mV]           0    -      65535
TYPE_GPS = 0x09            #  6 bytes  GPS lat & long       [binary]          3 lat + 3 long
TYPE_PULSE1 = 0x0A         #  2 bytes  Pulse input 1 rel    [n]            0    -      65535
TYPE_PULSE1_ABS = 0x0B     #  4 bytes  Pulse input 1 abs    [n]            0    - 4294967295
TYPE_EXT_TEMP1 = 0x0C      #  2 bytes  Ext temp 1           [°C]       -3276.5  -       3276.5
TYPE_EXT_DIGITAL = 0x0D    #  1 byte   Ext dig input 1      [bool]         0    -          1
TYPE_EXT_DISTANCE = 0x0E   #  2 bytes  Ext distance         [mm]           0    -      65535
TYPE_ACC_MOTION = 0x0F     #  1 byte   Motion (Acc mov)     [n]            0    -        255
TYPE_IR_TEMP = 0x10        #  4 bytes  IR temp              [°C]     2 int temp + 2 ext temp
TYPE_OCCUPANCY = 0x11      #  1 byte   Occupancy            [enum]         0    -          2
TYPE_WATERLEAK = 0x12      #  1 byte   Ext water leak       [conductivity] 0    -        255
TYPE_GRIDEYE = 0x13        # 65 bytes  Grideye data         []         1 ref + 64 pixel temp
TYPE_PRESSURE = 0x14       #  4 byte   Pressure             [hPa]          0    -       ????
TYPE_SOUND = 0x15          #  2 byte   Sound                [dB]              1 peak + 1 avg
TYPE_PULSE2 = 0x16         #  2 bytes  Pulse input 2 rel    [n]            0    -      65535
TYPE_PULSE2_ABS = 0x17     #  4 bytes  Pulse input 2 abs    [n]            0    - 4294967295
TYPE_ANALOG2 = 0x18        #  2 bytes  Analog input 2       [mV]           0    -      65535
TYPE_EXT_TEMP2 = 0x19      #  2 bytes  Ext temp 2           [°C]       -3276.5  -       3276.5
TYPE_EXT_DIGITAL2 = 0x1A   #  1 byte   Ext dig input 2      [bool]         0    -          1
TYPE_EXT_ANALOG_UV = 0x1B  #  4 bytes  Ext analog uV        [µV] −2147483648    - 2147483647
TYPE_DEBUG = 0x3D          #  4 bytes  Debug
TYPE_SETTINGS = 0x3E       #  n bytes  Sensor settings sent to server at startup (First package).
                           #           Sent on Port+1. See sensor settings document for more information.
TYPE_RFU = 0x3F            # Reserved for future use


def dict_from_payload(base64_input: str):
    decoded = base64.b64decode(base64_input)

    if DEBUG_OUTPUT:
        print(f"Input: {decoded.hex().upper()}")

    # Output
    result = {
        'error': False
    }

    # Iterate over the payload
    i = 0
    while i < len(decoded):
        if decoded[i] == TYPE_TEMP:  # Temperature
            temp = (decoded[i + 1] << 8) | (decoded[i + 2])
            temp = helpers.bin16dec(temp)
            result['temperature'] = temp / 10
            i += 3
        elif decoded[i] == TYPE_RH:  # Humidity
            rh = (decoded[i + 1])
            result['humidity'] = rh
            i += 2
        elif decoded[i] == TYPE_ACC:  # Acceleration X,Y,Z
            result['accX'] = helpers.bin8dec(decoded[i + 1])
            result['accY'] = helpers.bin8dec(decoded[i + 2])
            result['accZ'] = helpers.bin8dec(decoded[i + 3])
            i += 4
        elif decoded[i] == TYPE_LIGHT:  # Light
            result['light'] = (decoded[i + 1] << 8) | (decoded[i + 2])
            i += 3
        elif decoded[i] == TYPE_MOTION:  # Motion (PIR)
            result['motion'] = (decoded[i + 1])
            i += 2
        elif decoded[i] == TYPE_CO2:  # CO2
            result['co2'] = (decoded[i + 1] << 8) | (decoded[i + 2])
            i += 3
        elif decoded[i] == TYPE_VDD:  # Int battery voltage
            result['vdd'] = (decoded[i + 1] << 8) | (decoded[i + 2])
            i += 3
        elif decoded[i] == TYPE_ANALOG1:  # Analog input 1
            result['analog1'] = (decoded[i + 1] << 8) | (decoded[i + 2])
            i += 3
        elif decoded[i] == TYPE_GPS:  # GPS lat & long
            i += 1
            result['gpsLat'] = (decoded[i + 0] | decoded[i + 1] << 8 | decoded[i + 2] << 16 |
                                (0xFF << 24 if decoded[i + 2] & 0x80 else 0x00)) / 10000
            result['gpsLong'] = (decoded[i + 3] | decoded[i + 4] << 8 | decoded[i + 5] << 16 |
                                 (0xFF << 24 if decoded[i + 5] & 0x80 else 0x00)) / 10000
            i += 6
        elif decoded[i] == TYPE_PULSE1:  # Pulse input 1 rel
            result['pulse1'] = (decoded[i + 1] << 8) | (decoded[i + 2])
            i += 3
        elif decoded[i] == TYPE_PULSE1_ABS:  # Pulse input 1 abs
            result['pulse1Abs'] = (decoded[i + 1] << 24) | (decoded[i + 2] << 16) | \
                                 (decoded[i + 3] << 8) | (decoded[i + 4])
            i += 5
        elif decoded[i] == TYPE_EXT_TEMP1:  # Ext temp 1
            temp = (decoded[i + 1] << 8) | (decoded[i + 2])
            temp = helpers.bin16dec(temp)
            result['extTemp1'] = temp / 10
            i += 3
        elif decoded[i] == TYPE_EXT_DIGITAL:  # Ext dig input 1
            result['extDigital'] = (decoded[i + 1])
            i += 2
        elif decoded[i] == TYPE_EXT_DISTANCE:  # Ext distance
            result['extDistance'] = (decoded[i + 1] << 8) | (decoded[i + 2])
            i += 3
        elif decoded[i] == TYPE_ACC_MOTION:  # Motion (Acc mov)
            result['accMotion'] = (decoded[i + 1])
            i += 2
        elif decoded[i] == TYPE_IR_TEMP:  # IR temp
            iTemp = (decoded[i + 1] << 8) | (decoded[i + 2])
            iTemp = helpers.bin16dec(iTemp)
            eTemp = (decoded[i + 3] << 8) | (decoded[i + 4])
            eTemp = helpers.bin16dec(eTemp)
            result['irTempInt'] = iTemp / 10
            result['irTempExt'] = eTemp / 10
            i += 5
        elif decoded[i] == TYPE_OCCUPANCY:  # Occupancy
            result['occupancy'] = (decoded[i + 1])
            i += 2
        elif decoded[i] == TYPE_WATERLEAK:  # Ext water leak
            result['waterleak'] = (decoded[i + 1])
            i += 2
        elif decoded[i] == TYPE_GRIDEYE:  # Grideye data
            ref = decoded[i + 1]
            i += 1
            grideye = []
            for j in range(64):
                grideye[j] = ref + (decoded[1+i+j] / 10.0)
            i += 65
            result['grideye'] = grideye
        elif decoded[i] == TYPE_PRESSURE:  # Pressure
            temp = (decoded[i + 1] << 24) | (decoded[i + 2] << 16) | (decoded[i + 3] << 8) | (decoded[i + 4])
            result['pressure'] = temp / 1000
            i += 5
        elif decoded[i] == TYPE_SOUND:  # Sound
            result['soundPeak'] = decoded[i + 1]
            result['soundAvg'] = decoded[i + 2]
            i += 3
        elif decoded[i] == TYPE_PULSE2:  # Pulse input 2 rel
            result['pulse2'] = (decoded[i + 1] << 8) | (decoded[i + 2])
            i += 3
        elif decoded[i] == TYPE_PULSE2_ABS:  # Pulse input 2 abs
            result['pulse2Abs'] = (decoded[i + 1] << 24) | (decoded[i + 2] << 16) | \
                                  (decoded[i + 3] << 8) | (decoded[i + 4])
            i += 5
        elif decoded[i] == TYPE_ANALOG2:  # Analog input 2
            result['analog2'] = (decoded[i + 1] << 8) | (decoded[i + 2])
            i += 3
        elif decoded[i] == TYPE_EXT_TEMP2:  # Ext temp 2
            temp = (decoded[i + 1] << 8) | (decoded[i + 2])
            temp = helpers.bin16dec(temp)
            if 'extTemp2' in result:
                if type(result['extTemp2']) is float:
                    result['extTemp2'] = [result['extTemp2']]
                if type(result['extTemp2']) is list:
                    result['extTemp2'].append(temp / 10)
            else:
                result['extTemp2'] = temp / 10
            i += 3
        elif decoded[i] == TYPE_EXT_DIGITAL2:  # Ext dig input 2
            result['extDigital2'] = (decoded[i + 1])
            i += 2
        elif decoded[i] == TYPE_EXT_ANALOG_UV:  # Ext analog uV
            result['extAnalogUv'] = (decoded[i + 1] << 24) | (decoded[i + 2] << 16) | \
                                    (decoded[i + 3] << 8) | (decoded[i + 4])
            i += 5
        elif decoded[i] == TYPE_DEBUG:  # Debug
            result['debug'] = (decoded[i + 1] << 24) | (decoded[i + 2] << 16) | \
                              (decoded[i + 3] << 8) | (decoded[i + 4])
            i += 5
        elif decoded[i] == TYPE_SETTINGS:  # Sensor settings
            i = len(decoded)  # just ignore sensor settings packets
        else:  # something is wrong with the data
            result['error'] = True
            i = len(decoded)

    if DEBUG_OUTPUT:
        print(f"Output: {json.dumps(result,indent=2)}")

    return result


# Tests
if __name__ == "__main__":
    test_definition = [
        {
            "input_encoding": "hex",
            "input_value": "0100E202290400270506060308070D621900E21900A3",
            "output": {
                "temperature": 22.6,
                "humidity": 41,
                "light": 39,
                "motion": 6,
                "co2": 776,
                "vdd": 3426,
                "extTemp2": [
                    22.6,
                    16.3
                ],
                "error": False
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
