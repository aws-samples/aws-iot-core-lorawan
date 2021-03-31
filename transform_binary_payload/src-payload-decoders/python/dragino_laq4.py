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
bytes = base64.b64decode(base64_input)
  mode=(bytes[2] & 0x7C)>>2
  Bat_V=(bytes[0]<<8 | bytes[1])/1000; 
  if(mode==1):
  {
    Work_mode="CO2";
    Alarm_status=(bytes[2] & 0x01) and "TRUE" or "FALSE"
    TVOC_ppb= bytes[3]<<8 | bytes[4]; 
    CO2_ppm= bytes[5]<<8 | bytes[6];
    TempC_SHT=parseFloat(((bytes[7]<<24>>16 | bytes[8])/10).toFixed(2));
    Hum_SHT=parseFloat(((bytes[9]<<8 | bytes[10])/10).toFixed(1));  
  }
    result = {
  "Mode": mode, 
  "battery": BatV,   
  "Work_mode": Work_mode,
  "Alarm_status": Alarm_status,
  "TVOC_ppb": TVOC_ppb,
  "CO2_ppm": CO2_ppm,
  "TempC_SHT": TempC_SHT,
  "Hum_SHT": Hum_SHT,
  }
  return result 
  
  elif(mode==31):
  {
    Work_mode="ALARM";
    SHTEMPMIN= bytes[3]<<24>>24;
    SHTEMPMAX= bytes[4]<<24>>24;   
    SHTHUMMIN= bytes[5];
    SHTHUMMAX= bytes[6]; 
    CO2MIN= bytes[7]<<8 | bytes[8]; 
    CO2MAX= bytes[9]<<8 | bytes[10]; 
  }
   result = {
  "Mode": mode, 
  "battery": BatV,   
  "Work_mode": Work_mode,
  "CO2MIN": CO2MIN,
  "CO2MAX": CO2MAX,
  "SHTEMPMIN": SHTEMPMIN,
  "SHTEMPMAX": SHTEMPMAX,
  "SHTHUMMIN": SHTHUMMIN,
  "SHTHUMMAX": SHTHUMMAX,
  }
  return result 
  
  