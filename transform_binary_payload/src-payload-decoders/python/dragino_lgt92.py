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
import binascii


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
    bytes = base64.b64decode(base64_input)
    print(binascii.b2a_hex(bytes))
    lat = (bytes[0] << 24 | bytes[1] << 16 |
           bytes[2] << 8 | bytes[3]) / 1000000

    long = (bytes[4] << 24 | bytes[5] << 16 |
            bytes[6] << 8 | bytes[7]) / 1000000

    alarm = (bytes[8] & 0x40) > 0

    battery = ((bytes[8] & 0x3f) << 8 | bytes[9]) / 1000

    fw = 150+(bytes[10] & 0x1f)
    result = {
        "latitude": lat,
        "longitude": long,
        "alarm": alarm,
        "battery": battery,
        "firmware": fw

    }
    return result


# result = dict_from_payload("AuHtlACmawQPVGM=")
# print(str(result))
# print(result)
