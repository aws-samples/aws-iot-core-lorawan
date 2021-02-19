// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

// Permission is hereby granted, free of charge, to any person obtaining a copy of this
// software and associated documentation files (the "Software"), to deal in the Software
// without restriction, including without limitation the rights to use, copy, modify,
// merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
// permit persons to whom the Software is furnished to do so.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
// INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
// PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
// HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
// OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
// SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

function decodeUplink(input) {
    bytes = input.bytes
    port = input.fPort

    return {
        data: {

            //External sensor
            // ext_sensor_type:
            //     {
            //         "0": "No external sensor",
            //         "1": "Temperature Sensor",
            //         "4": "Interrupt Sensor send",
            //         "5": "Illumination Sensor",
            //         "6": "ADC Sensor",
            //         "7": "Interrupt Sensor count",
            //     }[bytes[6] & 0x7F],

            //Battery,units:V
            battery_value: ((bytes[0] << 8 | bytes[1]) & 0x3FFF) / 1000,

            //SHT20,temperature
            temperature_internal: (bytes[2] << 24 >> 16 | bytes[3]) / 100,

            //SHT20,Humidity,units:%
            humidity: (bytes[4] << 8 | bytes[5]) / 10,

            //DS18B20,temperature,units:
            temperature_external:
                ((bytes[7] << 24 >> 16 | bytes[8]) / 100),



        }
    };
}

module.exports = { decodeUplink }