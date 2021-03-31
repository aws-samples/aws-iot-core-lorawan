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
  hardware= (bytes[10] & 0xC0)>>6
  mode0= bytes[10] & 0xff
  mode= bytes[10] & 0x3f
  
  if(hardware=='0'):
  {
    Hardware_mode="LT33222";
    DO3_status=((bytes[8] &0x04)==4) and "L" or "H"
    if(mode0=='1'):
    {
      DI3_status=((bytes[8] &0x20)==32) and "H" or "L"
    }
    result = {
            "Mode": mode, 
            "Hardware_mode": Hardware_mode,
            "DO3_status": DO3_status,
            "DI3_status": DI3_status,
        }

        return result
  }
  elif(hardware=='1'):
  {
    Hardware_mode= "LT22222";
  }

  result = {
            "Mode": mode, 
            "Hardware_mode": Hardware_mode,
        }

        return result

  if(mode!=6):
  {
    DO1_status=((bytes[8] &0x01)==1) and "L" or "H"
    DO2_status=((bytes[8] &0x02)==2) and "L" or "H"
    RO1_status=((bytes[8] &0x80)==128) and "ON" or "OFF"
    RO2_status=((bytes[8] &0x40)==64) and "ON" or "OFF"
    if(mode!=1):
    {
      if(mode!=5):
      {
       Count1_times= (bytes[0]<<24 | bytes[1]<<16 | bytes[2]<<8 | bytes[3]);
      }
      First_status=((bytes[8] &0x20)==32) and "Yes" or "No"
    }
  }
  result = {
            "DO1_status": DO1_status, 
            "DO2_status": DO2_status,
            "RO1_status": RO1_status,
            "RO2_status": RO2_status,
            "Count1_times": Count1_times, 
            "First_status": First_status,
        }

        return result

  if(mode=='1'):
  {
    Work_mode= "2ACI+2AVI";
    AVI1_V= parseFloat(((bytes[0]<<24>>16 | bytes[1])/1000).toFixed(3));
    AVI2_V= parseFloat(((bytes[2]<<24>>16 | bytes[3])/1000).toFixed(3));
    ACI1_mA= parseFloat(((bytes[4]<<24>>16 | bytes[5])/1000).toFixed(3));
    ACI2_mA= parseFloat(((bytes[6]<<24>>16 | bytes[7])/1000).toFixed(3));
    DI1_status=((bytes[8] &0x08)==8) and "H" or "L"
    DI2_status=((bytes[8] &0x10)==16) and "H" or "L"
  }
  result = {
            "Work_mode": Work_mode, 
            "AVI1_V": AVI1_V,
            "AVI2_V": AVI2_V,
            "ACI1_mA": ACI1_mA,
            "ACI2_mA": ACI2_mA, 
            "DI1_status": DI1_status,
            "DI2_status": DI2_status,
        }

        return result

  elif(mode=='2'):
  {
    Work_mode= "Count mode 1";
    Count2_times= (bytes[4]<<24 | bytes[5]<<16 | bytes[6]<<8 | bytes[7]);
  }
  result = {
            "Work_mode": Work_mode, 
            "Count2_times": Count2_times,
        }

        return result

  elif(mode=='3'):
  {
    Work_mode= "2ACI+1Count";
    ACI1_mA= parseFloat(((bytes[4]<<24>>16 | bytes[5])/1000).toFixed(3));
    ACI2_mA= parseFloat(((bytes[6]<<24>>16 | bytes[7])/1000).toFixed(3));
  }
  result = {
            "Work_mode": Work_mode, 
            "ACI1_mA": ACI1_mA,
            "ACI2_mA": ACI2_mA, 
        }

        return result

  elif(mode=='4'):
  {
    Work_mode= "Count mode 2";
    Acount_times= (bytes[4]<<24 | bytes[5]<<16 | bytes[6]<<8 | bytes[7]);
  }
  result = {
            "Work_mode": Work_mode, 
            "Acount_times": Acount_times,
        }

        return result

  elif(mode=='5'):
  {
    Work_mode= " 1ACI+2AVI+1Count";
    AVI1_V= parseFloat(((bytes[0]<<24>>16 | bytes[1])/1000).toFixed(3));
    AVI2_V= parseFloat(((bytes[2]<<24>>16 | bytes[3])/1000).toFixed(3));
    ACI1_mA= parseFloat(((bytes[4]<<24>>16 | bytes[5])/1000).toFixed(3));
    Count1_times= bytes[6]<<8 | bytes[7];
  }
  result = {
            "Work_mode": Work_mode, 
            "AVI1_V": AVI1_V,
            "AVI2_V": AVI2_V,
            "ACI1_mA": ACI1_mA,
            "Count1_times": Count1_times,
        }

        return result

  elif(mode=='6'):
  {
    Work_mode= "Exit mode"; 
    Mode_status=(bytes[9]==0) and "False" or "True"
    AV1L_flag=((bytes[0] &0x80)==128) and "True" or "False"
    AV1H_flag=((bytes[0] &0x40)==64) and "True" or "False"
    AV2L_flag=((bytes[0] &0x20)==32) and "True" or "False"
    AV2H_flag=((bytes[0] &0x10)==16) and "True" or "False"
    AC1L_flag=((bytes[0] &0x08)==8) and "True" or "False"
    AC1H_flag=((bytes[0] &0x04)==4) and "True" or "False"
    AC2L_flag=((bytes[0] &0x02)==2) and "True" or "False"
    AC2H_flag=((bytes[0] &0x01)==1) and "True" or "False"
    AV1L_status=((bytes[1] &0x80)==128) and "True" or "False"
    AV1H_status=((bytes[1] &0x40)==64) and "True" or "False"
    AV2L_status=((bytes[1] &0x20)==32) and "True" or "False" 
    AV2H_status=((bytes[1] &0x10)==16) and "True" or "False"
    AC1L_status=((bytes[1] &0x08)==8) and "True" or "False"
    AC1H_status=((bytes[1] &0x04)==4) and "True" or "False"
    AC2L_status=((bytes[1] &0x02)==2) and "True" or "False" 
    AC2H_status=((bytes[1] &0x01)==1) and "True" or "False"
    DI2_status=((bytes[2] &0x08)==8) and "True" or "False"
    DI2_flag=((bytes[2] &0x04)==4) and "True" or "False"
    DI1_status=((bytes[2] &0x02)==2) and "True" or "False" 
    DI1_flag=((bytes[2] &0x01)==1) and "True" or "False"
  }
  result = {
            "Work_mode": Work_mode, 
            "Mode_status": Mode_status,
            "AV1L_flag": AV1L_flag,
            "AV1H_flag": AV1H_flag,
            "AV2L_flag": AV2L_flag,
            "AV2H_flag": AV2H_flag, 
            "AC1L_flag": AC1L_flag,
            "AC1H_flag": AC1H_flag,
            "AC2L_flag": AC2L_flag,
            "AC2H_flag": AC2H_flag, 
            "AV1L_status": AV1L_status,
            "AV1H_status": AV1H_status,
            "AV2L_status": AV2L_status,
            "AV2H_status": AV2H_status,
            "AC1L_status": AC1L_status, 
            "AC1H_status": AC1H_status,
            "AC2L_status": AC2L_status,
            "AC2H_status": AC2H_status,
            "DI2_status": DI2_status,
            "DI2_flag": DI2_flag, 
            "DI1_status": DI1_status,
            "DI1_flag": DI1_flag,
        }

        return result
    
  
