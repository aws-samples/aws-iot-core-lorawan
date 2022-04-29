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
		// Decode an uplink message from a buffer
		// (array) of bytes to an object of fields.
		var value=(bytes[0]<<8 | bytes[1]) & 0x3FFF;
		var batV=value/1000;//Battery,units:V

		value=bytes[2]<<8 | bytes[3];
		if(bytes[2] & 0x80)
		{value |= 0xFFFF0000;}
		var temp_DS18B20=(value/10).toFixed(2);//DS18B20,temperature

		value=bytes[4]<<8 | bytes[5];
		var PH1=(value/100).toFixed(2);

		value=bytes[6]<<8 | bytes[7];
		var temp=0;
		if((value & 0x8000)>>15 === 0)
			temp=(value/10).toFixed(2);//temp_SOIL,temperature
		else if((value & 0x8000)>>15 === 1)
			temp=((value-0xFFFF)/10).toFixed(2);

		var i_flag = bytes[8];
		var mes_type = bytes[10];
    return {
		data: {
			Bat:batV,
			TempC_DS18B20:temp_DS18B20,
			PH1_SOIL:PH1,
			TEMP_SOIL:temp,
			Interrupt_flag:i_flag,
			Message_type:mes_type
		}
    };
}