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


// Cayenne LPP Format Quick Reference
/**
 * https://github.com/myDevicesIoT/cayenne-docs/blob/master/docs/LORA.md
 * 
 * Type                 IPSO    LPP     Hex     Data Size   Data Resolution per bit
 *  Digital Input       3200    0       0       1           1
 *  Digital Output      3201    1       1       1           1
 *  Analog Input        3202    2       2       2           0.01 Signed
 *  Analog Output       3203    3       3       2           0.01 Signed
 *  Illuminance Sensor  3301    101     65      2           1 Lux Unsigned MSB
 *  Presence Sensor     3302    102     66      1           1
 *  Temperature Sensor  3303    103     67      2           0.1 °C Signed MSB
 *  Humidity Sensor     3304    104     68      1           0.5 % Unsigned
 *  Accelerometer       3313    113     71      6           0.001 G Signed MSB per axis
 *  Barometer           3315    115     73      2           0.1 hPa Unsigned MSB
 *  Gyrometer           3334    134     86      6           0.01 °/s Signed MSB per axis
 *  GPS Location        3336    136     88      9           Latitude  : 0.0001 ° Signed MSB
 *                                                          Longitude : 0.0001 ° Signed MSB
 *                                                          Altitude  : 0.01 meter Signed MSB
 */

function arrayToDecimal(stream, is_signed=false, decimal_point=0) {
    var value = 0;
    for (var i = 0; i < stream.length; i++) {
        if (stream[i] > 0xFF) 
            throw 'Byte value overflow!';
        value = (value<<8) | stream[i];
    }
    
    if (is_signed) {
        edge  = 1 << (stream.length  )*8;  // 0x1000..
        max   = (edge-1) >> 1;             // 0x0FFF.. >> 1
        value = (value > max) ? value - edge : value;
    }    
    
    if (decimal_point) {
        value /= Math.pow(10, decimal_point);
    }
    
    return value;
}

function decode(payload) {
   
    var sensor_types = { 
            0  : {'size': 1, 'name': 'Digital Input'      , 'signed': false, 'decimal_point': 0,},
            1  : {'size': 1, 'name': 'Digital Output'     , 'signed': false, 'decimal_point': 0,},
            2  : {'size': 2, 'name': 'Analog Input'       , 'signed': true , 'decimal_point': 2,},
            3  : {'size': 2, 'name': 'Analog Output'      , 'signed': true , 'decimal_point': 2,},
            101: {'size': 2, 'name': 'Illuminance Sensor' , 'signed': false, 'decimal_point': 0,},
            102: {'size': 1, 'name': 'Presence Sensor'    , 'signed': false, 'decimal_point': 0,},
            103: {'size': 2, 'name': 'Temperature Sensor' , 'signed': true , 'decimal_point': 1,},
            104: {'size': 1, 'name': 'Humidity Sensor'    , 'signed': false, 'decimal_point': 1,},
            113: {'size': 6, 'name': 'Accelerometer'      , 'signed': true , 'decimal_point': [3,3,3]},
            115: {'size': 2, 'name': 'Barometer'          , 'signed': false, 'decimal_point': 1,},
            134: {'size': 6, 'name': 'Gyrometer'          , 'signed': true , 'decimal_point': [2,2,2]},
            136: {'size': 9, 'name': 'GPS Location'       , 'signed': true, 'decimal_point': [4,4,2], },};
    
    var sensors = {};
    var i = 0;
	while (i < payload.length) {
	    // console.log(i);
	    // console.log(typeof payload[i])
	    // console.log(payload[i].toString())
	    s_no   = payload[i++];
		s_type = payload[i++];
		if (typeof sensor_types[s_type] == 'undefined')
		    throw format('Sensor type error!: {}', s_type);	
	    s_size = sensor_types[s_type].size;
	    s_name = sensor_types[s_type].name;
	    
	    switch (s_type) {
    	    case 0  :  // Digital Input
            case 1  :  // Digital Output
            case 2  :  // Analog Input
            case 3  :  // Analog Output
            case 101:  // Illuminance Sensor
            case 102:  // Presence Sensor
            case 103:  // Temperature Sensor
            case 104:  // Humidity Sensor
            case 115:  // Barometer
                s_value = arrayToDecimal(payload.slice(i, i+s_size), 
                        is_signed     = sensor_types[s_type].signed, 
                        decimal_point = sensor_types[s_type].decimal_point);                
                // Resolution fix for humidity - at 0.5
                if (s_type == 104) { s_value = s_value * 5};
                break;
            case 113: //Accel
                s_value = {
                    'x': arrayToDecimal(payload.slice(i+0, i+2), is_signed=sensor_types[s_type].signed, decimal_point=sensor_types[s_type].decimal_point[0]),
                    'y': arrayToDecimal(payload.slice(i+2, i+4), is_signed=sensor_types[s_type].signed, decimal_point=sensor_types[s_type].decimal_point[1]),
                    'z': arrayToDecimal(payload.slice(i+4, i+6), is_signed=sensor_types[s_type].signed, decimal_point=sensor_types[s_type].decimal_point[2]),
                };
                break;
            case 134: // Gyro
                s_value = {
                    'x': arrayToDecimal(payload.slice(i+0, i+2), is_signed=sensor_types[s_type].signed, decimal_point=sensor_types[s_type].decimal_point[0]),
                    'y': arrayToDecimal(payload.slice(i+2, i+4), is_signed=sensor_types[s_type].signed, decimal_point=sensor_types[s_type].decimal_point[1]),
                    'z': arrayToDecimal(payload.slice(i+4, i+6), is_signed=sensor_types[s_type].signed, decimal_point=sensor_types[s_type].decimal_point[2]),
                };
                break;
            case 136:  // GPS Location
                s_value = {
                        'latitude':  arrayToDecimal(payload.slice(i+0, i+3), is_signed=sensor_types[s_type].signed, decimal_point=sensor_types[s_type].decimal_point[0]), 
                        'longitude': arrayToDecimal(payload.slice(i+3, i+6), is_signed=sensor_types[s_type].signed, decimal_point=sensor_types[s_type].decimal_point[1]), 
                        'altitude':  arrayToDecimal(payload.slice(i+6, i+9), is_signed=sensor_types[s_type].signed, decimal_point=sensor_types[s_type].decimal_point[2]),};
                break;
        }
	    
	    sensors[s_no] = {'type': s_type, 'type_name': s_name, 'value': s_value };
	    i += s_size;
	}
	
	return sensors;
}

module.exports = decode;
