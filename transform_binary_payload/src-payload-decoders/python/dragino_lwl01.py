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
    value= (bytes[0] << 8 | bytes[1]) & 0x3FFF
    battery = value/1000
    door_open_status = 0

    if bytes[0] & 0x40:
        water_leak_status = 1

    water_leak_status = 0
    if bytes[0] & 0x80:
        door_open_status = 1

    mod = bytes[2]

    if mod == 1:
        open_times = bytes[3] << 16 | bytes[4] << 8 | bytes[5]
        open_duration = bytes[6] << 16 | bytes[7] << 8 | bytes[8]
        result = {
            "mod": mod,
            "battery": battery,
            "door_open_status": door_open_status,
            "open_times": open_times,
            "open_duration": open_duration
        }

        return result

    if mod == 2:
        leak_times = bytes[3] << 16 | bytes[4] << 8 | bytes[5]
        leak_duration = bytes[6] << 16 | bytes[7] << 8 | bytes[8]

        result = {
            "mod": mod,
            "battery": battery,
            "leak_times": leak_times,
            "leak_duration": leak_duration
        }

        return result

    result = {
        "battery": battery,
        "mod": mod
    }