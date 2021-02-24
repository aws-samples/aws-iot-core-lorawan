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

const AWS = require('aws-sdk');
var decode = require('./cayennelpp');
exports.main = async function(event, context) {
    console.log(event);
    var gateways = event.WirelessMetadata.LoRaWAN.Gateways;
    gateways.forEach(function(gateway) {
        console.log(gateway);
    });

    console.log(event.PayloadData);
    var PayloadData = event.PayloadData;
    var data = Buffer.from(PayloadData, 'base64');
    var values = Object.values(decode(data));
    var data = {};
    
    // Add an incoming timestamp in the Lambda
    data.timestamp = new Date().getTime();
    data.DevEUI = event.WirelessMetadata.LoRaWAN.DevEui;
    data.DeviceId = event.WirelessMetadata.LoRaWAN.DevEui;
    data.datetime = event.WirelessMetadata.LoRaWAN.Timestamp;

    values.forEach(function (sensorEntry){
        // console.log(sensorEntry.type);
        // console.log(sensorEntry.value);
        switch(sensorEntry.type) {
            case 0: // CNT field being sent in DigitalInput
                data.count = sensorEntry.value;
                break;
            case 101:       // Illumance Sensor
                data.lux = sensorEntry.value;
                break;
            case 102:
                data.presence = sensorEntry.value;
                break;
            case 103:
                data.temperature = sensorEntry.value;
                break;
            case 104:
                data.humidity = sensorEntry.value;
                break;
            case 115:
                data.pressure = sensorEntry.value;
                break;
            case 113:
                var accel = {};
                accel.x = sensorEntry.value.x;
                accel.y = sensorEntry.value.y;
                accel.z = sensorEntry.value.z;
                data.accel = accel;
                break;
            case 134:
                var gyro = {};
                gyro.x = sensorEntry.value.x;
                gyro.y = sensorEntry.value.y;
                gyro.z = sensorEntry.value.z;
                data.gyro = gyro;
                break;
            case 136:       // GPS
                var loc = {};
                loc.lat = sensorEntry.value.latitude;
                loc.lng = sensorEntry.value.longitude;
                loc.alt = sensorEntry.value.altitude;
                data.loc = loc;
                break;
            default:
                console.log('Something messed up, type not handled.')
                break;
        };
    });

    console.log(data);
    return data;
}