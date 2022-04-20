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

    bytes = base64.b64decode(base64_input)
    mode=(bytes[6] & 0x7C)>>2
    if(mode!=2)and(mode!=31):
        {
        BatV=(bytes[0]<<8 | bytes[1])/1000
        TempC1= parseFloat(((bytes[2]<<24>>16 | bytes[3])/10).toFixed(2))
        ADC_CH0V=(bytes[4]<<8 | bytes[5])/1000
        Digital_IStatus=((bytes[6] & 0x02)==2) and "H" or "L"
        if(mode!=6):
            {
            EXTI_Trigger=((bytes[6] & 0x01)==1) and "TRUE" or "FALSE"
            Door_status=((bytes[6] & 0x80)==128) and "CLOSE" or "OPEN"
        }
    }
    result = {
        "Mode": mode, 
        "TempC1": TempC1,
        "battery": BatV,
        "ADC_CH0V": ADC_CH0V,
        "Digital_IStatus": Digital_IStatus
        "EXTI_Trigger": EXTI_Trigger
        "Door_status": Door_status
    }

    return result


    if(mode=='0'):
        {
        Work_mode="IIC";
        if((bytes[9]<<8 | bytes[10])===0):
            {
                Illum=(bytes[7]<<24>>16 | bytes[8]);
        }
        else:
            {
            TempC_SHT=parseFloat(((bytes[7]<<24>>16 | bytes[8])/10).toFixed(2));
            Hum_SHT=parseFloat(((bytes[9]<<8 | bytes[10])/10).toFixed(1));
        }
        result = {
            "Work_mode": Work_mode,
            "Illum": Illum,
            "TempC_SHT": TempC_SHT
            "Hum_SHT": Hum_SHT
        }

        return result
    }
    elif(mode=='1'):
        {
        Work_mode=" Distance";
        Distance_cm=parseFloat(((bytes[7]<<8 | bytes[8])/10) .toFixed(1));
        if((bytes[9]<<8 | bytes[10])!=65535):
            {
                Distance_signal_strength=parseFloat((bytes[9]<<8 | bytes[10]) .toFixed(0));
        }
    }
    result = {
        "Work_mode": Work_mode,
        "Distance_cm": Distance_cm,
        "Distance_signal_strength": Distance_signal_strength
    }

    return result

    elif(mode=='2'):
        {
        Work_mode=" 3ADC";
        BatV=bytes[11]/10;
        ADC_CH0V=(bytes[0]<<8 | bytes[1])/1000;
        ADC_CH1V=(bytes[2]<<8 | bytes[3])/1000;
        ADC_CH4V=(bytes[4]<<8 | bytes[5])/1000;
        Digital_IStatus=((bytes[6] & 0x02)==2) and "H" or "L"
        EXTI_Trigger=((bytes[6] & 0x01)==1) and "TRUE" or "FALSE"
        Door_status=((bytes[6] & 0x80)==128) and "CLOSE" or "OPEN"
        if((bytes[9]<<8 | bytes[10])===0):
            {
                Illum=(bytes[7]<<24>>16 | bytes[8]);
        }
        else:
            {
            TempC_SHT=parseFloat(((bytes[7]<<24>>16 | bytes[8])/10).toFixed(2));
            Hum_SHT=parseFloat(((bytes[9]<<8 | bytes[10])/10) .toFixed(1));
        }
    }
    result = {
        "Mode": mode,
        "Work_mode": Work_mode,
        "battery": BatV,
        "ADC_CH0V": ADC_CH0V,
        "ADC_CH1V": ADC_CH1V,
        "ADC_CH4V": ADC_CH4V,
        "Digital_IStatus": Digital_IStatus
        "EXTI_Trigger": EXTI_Trigger
        "Door_status": Door_status
        "Illum": Illum,
        "TempC_SHT": TempC_SHT
        "Hum_SHT": Hum_SHT
    }

    return result

    elif(mode=='3'):
        {
        Work_mode="3DS18B20";
        TempC2=parseFloat(((bytes[7]<<24>>16 | bytes[8])/10).toFixed(2));
        TempC3=parseFloat(((bytes[9]<<8 | bytes[10])/10) .toFixed(1));
    }
    result = {
        "Work_mode": Work_mode,
        "TempC2": TempC1,
        "TempC3": TempC1,
    }
    return result

    elif(mode=='4'):
        {
        Work_mode="Weight";
        Weight=(bytes[7]<<24>>16 | bytes[8]);
    }
    result = {
        "Work_mode": Work_mode,
        "Weight": Weight,
    }
    return result

    elif(mode=='5'):
        {
        Work_mode="Count";
        Count=(bytes[7]<<24 | bytes[8]<<16 | bytes[9]<<8 | bytes[10]);
    }
    result = {
        "Work_mode": Work_mode,
        "Count": Count,
    }
    return result

    elif(mode=='31'):
        { 
        Work_mode="ALARM";
        BatV=(bytes[0]<<8 | bytes[1])/1000;
        TempC1= parseFloat(((bytes[2]<<24>>16 | bytes[3])/10).toFixed(2));
        TempC1MIN= bytes[4]<<24>>24;
        TempC1MAX= bytes[5]<<24>>24; 
        SHTEMPMIN= bytes[7]<<24>>24;
        SHTEMPMAX= bytes[8]<<24>>24;   
        SHTHUMMIN= bytes[9];
        SHTHUMMAX= bytes[10];   
    }
    result = {
        "Mode": mode,
        "Work_mode": Work_mode,
        "TempC1": TempC1,
        "battery": BatV,
        "TempC1MIN": TempC1MIN,
        "TempC1MAX": TempC1MAX,
        "SHTEMPMIN": SHTEMPMIN,
        "SHTEMPMAX": SHTEMPMAX,
        "SHTHUMMIN": SHTHUMMIN,
        "SHTHUMMAX": SHTHUMMAX,
    }
    return result