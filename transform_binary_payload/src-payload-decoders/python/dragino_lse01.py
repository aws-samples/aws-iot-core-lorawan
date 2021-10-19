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

    value = (decoded[0] << 8 | decoded[1]) & 0x3FFF
    battery_value = value/1000  # /Battery,units:V

    value = decoded[2] << 8 | decoded[3]
    if decoded[2] & 0x80:
        value |= 0xFFFF0000

    temp_DS18B20 = (value/10)  # /DS18B20,temperature,units:℃

    value = decoded[4] << 8 | decoded[5]
    water_SOIL = (value/100)  # /water_SOIL,Humidity,units:%

    value = decoded[6] << 8 | decoded[7]

    if ((value & 0x8000) >> 15) == 0:
        temp_SOIL = (value/100)  # /temp_SOIL,temperature,units:°C
    elif ((value & 0x8000) >> 15) == 1:
        temp_SOIL = ((value-0xFFFF)/100)

    value = decoded[8] << 8 | decoded[9]
    conduct_SOIL = (value/100)  # /conduct_SOIL,conductivity,units:uS/cm

    result = {
        "battery_value": battery_value,
        "temperature_internal": temp_DS18B20,
        "water_soil":  water_SOIL,
        "temperature_soil":  temp_SOIL,
        "conduct_soil": conduct_SOIL

    }
    return result