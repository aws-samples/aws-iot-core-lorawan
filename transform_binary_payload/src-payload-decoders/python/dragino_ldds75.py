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

     len=decoded.length
  value=(decoded[0]<<8 | decoded[1]) & 0x3FFF
  batV=value/1000
  distance = 0
  if(len==5): 
  {
   value=decoded[2]<<8 | decoded[3]
   distance=(value)
   if(value<20):
    distance = "Invalid Reading"
  }
  else:
   distance = "No Sensor" 
   interrupt = decoded[len-1]
  result ={
       "Bat":batV ,
       "Distance":distance,
       "Interrupt_status":interrupt
  }

return result
