def bin32dec(binary):
    number = binary & 0xFFFFFFFF
    if 0x80000000 & number:
        number = -(0x0100000000 - number)
    return number


def bin16dec(binary):
    number = binary & 0xFFFF
    if 0x8000 & number:
        number = -(0x010000 - number)
    return number


def bin8dec(binary):
    number = binary & 0xFF
    if 0x80 & number:
        number = -(0x0100 - number)
    return number


def is_single_bit_set(number):
    """
    Return True if number has exactly one bit set to 1; False
    if it has any other number of bits set to 1.
    """
    # Special case for zero
    if number == 0:
        return False
    return number & (number - 1) == 0


def bytes_to_float(decoded, start_index, length) -> float:
    """ Decodes two or four bytes of the ByteString to a precise float
        The start_index sets the first (two) byte(s) in the decoded payload for the fractional value.
    Parameters
    ----------
    decoded : ByteString
        payload
    start_index: int
        Index to set the starting point in the ByteString
    length: int
        Integer value to set the length of bytes which have the needed data for integer and fractional variable
        e.g. length=2 -> one byte for fractional and one byte for integer value
        e.g. length=4 -> two bytes for fractional and two bytes for integer value
        length must be of value 2 or 4
    Returns
    -------
    float
    """
    if length == 2:
        # Fractional part
        fractional = bin8dec(decoded[start_index])
        # Integer part
        integer = bin8dec(decoded[start_index + 1])
    elif length == 4:
        # Fractional portion
        fractional = bin16dec(decoded[start_index] << 8 | decoded[start_index + 1])
        # Integer portion
        integer = bin16dec(decoded[start_index + 2] << 8 | decoded[start_index + 3])
    else:
        raise ValueError("Wrong value for parameter length")

    return integer + (fractional / 100)
