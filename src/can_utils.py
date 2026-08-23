import socket
import struct
import time


CAN_INTERFACE = "vcan0"


def create_can_socket():
    """Create and bind a raw CAN socket to vcan0."""
    sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    sock.bind((CAN_INTERFACE,))
    return sock


def send_message(sock, can_id, data):
    """Send a CAN frame."""
    if len(data) > 8:
        raise ValueError("CAN payload cannot exceed 8 bytes")

    frame = struct.pack(
        "=IB3x8s",
        can_id,
        len(data),
        data.ljust(8, b"\x00")
    )

    sock.send(frame)


def receive_message(sock):
    """Receive and decode a CAN frame."""
    frame = sock.recv(16)

    can_id, data_length, data = struct.unpack(
        "=IB3x8s",
        frame
    )

    return can_id, data[:data_length]


def encode_uint8(value):
    """Encode an unsigned 8-bit integer."""
    if not 0 <= value <= 255:
        raise ValueError("Value must be between 0 and 255")

    return struct.pack("B", value)


def decode_uint8(data):
    """Decode an unsigned 8-bit integer."""
    if len(data) < 1:
        raise ValueError("CAN data is empty")

    return struct.unpack("B", data[:1])[0]


def encode_uint16(value):
    """Encode an unsigned 16-bit integer using big-endian encoding."""
    if not 0 <= value <= 65535:
        raise ValueError("Value must be between 0 and 65535")

    return struct.pack(">H", value)


def decode_uint16(data):
    """Decode an unsigned 16-bit integer using big-endian encoding."""
    if len(data) < 2:
        raise ValueError("CAN data must contain at least 2 bytes")

    return struct.unpack(">H", data[:2])[0]


def timestamp():
    """Return a formatted timestamp for diagnostic logging."""
    return time.strftime("%Y-%m-%d %H:%M:%S")
