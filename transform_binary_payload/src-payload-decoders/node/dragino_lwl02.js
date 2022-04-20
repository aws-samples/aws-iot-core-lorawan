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
  var value=(bytes[0]<<8 | bytes[1])&0x3FFF;
  var bat=value/1000;//Battery,units:V
  
  var door_open_status=bytes[0]&0x80?1:0;//1:open,0:close
  var water_leak_status=bytes[0]&0x40?1:0;
  
  var mod=bytes[2];
  var alarm=bytes[9]&0x01;
  
  if(mod==1){
    var open_times=bytes[3]<<16 | bytes[4]<<8 | bytes[5];
    var open_duration=bytes[6]<<16 | bytes[7]<<8 | bytes[8];//units:min
    if(bytes.length==10 &&  0x07>bytes[0]< 0x0f)
    return {
      data: {
        BAT_V:bat,
        MOD:mod,
        DOOR_OPEN_STATUS:door_open_status,
        DOOR_OPEN_TIMES:open_times,
        LAST_DOOR_OPEN_DURATION:open_duration,
        ALARM:alarm
      }
    };
  }
  else if(mod==2)
  {
    var leak_times=bytes[3]<<16 | bytes[4]<<8 | bytes[5];
    var leak_duration=bytes[6]<<16 | bytes[7]<<8 | bytes[8];//units:min
    if(bytes.length==10 &&  0x07>bytes[0]< 0x0f)
    return {
      data: {
        BAT_V:bat,
        MOD:mod,
        WATER_LEAK_STATUS:water_leak_status,
        WATER_LEAK_TIMES:leak_times,
        LAST_WATER_LEAK_DURATION:leak_duration
      }
    };
  }
  else if(mod==3)
  if(bytes.length==10 &&  0x07>bytes[0]< 0x0f)
  {
    return {
      data: {
          BAT_V:bat,
          MOD:mod,
          DOOR_OPEN_STATUS:door_open_status,
          WATER_LEAK_STATUS:water_leak_status,
          ALARM:alarm
        }
    };
  }
  else{
  return {
    data: {
        BAT_V:bat,
        MOD:mod,
      }
  };
  }
}
