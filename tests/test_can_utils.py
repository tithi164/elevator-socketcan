from src.can_utils import (
    encode_uint8,
    decode_uint8,
    encode_uint16,
    decode_uint16,
)


def main():
    value8 = 5
    encoded8 = encode_uint8(value8)
    decoded8 = decode_uint8(encoded8)

    assert decoded8 == value8

    value16 = 0x0006
    encoded16 = encode_uint16(value16)
    decoded16 = decode_uint16(encoded16)

    assert decoded16 == value16

    print("CAN encoding tests passed")


if __name__ == "__main__":
    main()
