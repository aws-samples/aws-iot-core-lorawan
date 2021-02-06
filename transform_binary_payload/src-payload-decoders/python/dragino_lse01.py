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

    value = (decoded[0] << 8 | decoded[1]) & 0x3FFF
    battery_value = value  # /Battery,units:V

    value = decoded[2] << 8 | decoded[3]
    if(decoded[2] & 0x80):
        value |= 0xFFFF0000

    temp_DS18B20 = (value/10)  # /DS18B20,temperature,units:℃

    value = decoded[4] << 8 | decoded[5]
    water_SOIL = (value/100)  # /water_SOIL,Humidity,units:%

    value = decoded[6] << 8 | decoded[7]

    if((value & 0x8000) >> 15 == 0):
        temp_SOIL = (value/100)  # /temp_SOIL,temperature,units:°C
    elif((value & 0x8000) >> 15 == 1):
        temp_SOIL = ((value-0xFFFF)/100)

    value = decoded[8] << 8 | decoded[9]
    conduct_SOIL = (value/100)  # /conduct_SOIL,conductivity,units:uS/cm

    result = {
        "battery_value": battery_value,
        "temperature_internal": temp_DS18B20,
        "water_soil":  water_SOIL,
        "temperature_soil":  temp_SOIL,
        "conduct_soil": conduct_SOIL

    }
    return result
