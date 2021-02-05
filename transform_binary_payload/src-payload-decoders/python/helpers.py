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
