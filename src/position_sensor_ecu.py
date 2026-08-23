import select
import time

from src.can_utils import (
    create_can_socket,
    send_message,
    receive_message,
    encode_uint8,
    decode_uint8,
)


CURRENT_FLOOR_ID = 0x101
POSITION_STATUS_ID = 0x102
MOTOR_STATUS_ID = 0x103
HEARTBEAT_ID = 0x111

MIN_FLOOR = 1
MAX_FLOOR = 5

POSITION_UNKNOWN = 0
POSITION_VALID = 1
POSITION_INVALID = 2
POSITION_SENSOR_FAULT = 3

MOTOR_STOPPED = 0
MOTOR_MOVING_UP = 1
MOTOR_MOVING_DOWN = 2

TRANSMISSION_PERIOD = 0.1
HEARTBEAT_PERIOD = 0.2


def send_current_floor(sock, floor):
    send_message(
        sock,
        CURRENT_FLOOR_ID,
        encode_uint8(floor)
    )


def send_position_status(sock, status):
    send_message(
        sock,
        POSITION_STATUS_ID,
        encode_uint8(status)
    )


def send_heartbeat(sock, counter):
    send_message(
        sock,
        HEARTBEAT_ID,
        encode_uint8(counter)
    )


def main():
    sock = create_can_socket()
    sock.setblocking(False)

    current_floor = 1
    motor_status = MOTOR_STOPPED

    heartbeat_counter = 0

    last_transmission = time.monotonic()
    last_heartbeat = time.monotonic()
    last_movement = time.monotonic()

    print("--------------------------------")
    print("       Position/Sensor ECU")
    print("--------------------------------")
    print("SocketCAN interface: vcan0")
    print(f"Initial floor: {current_floor}")
    print("--------------------------------")

    try:
        while True:
            readable, _, _ = select.select(
                [sock],
                [],
                [],
                0.02
            )

            if readable:
                try:
                    can_id, data = receive_message(sock)

                    if can_id == MOTOR_STATUS_ID and data:
                        motor_status = decode_uint8(data)

                except BlockingIOError:
                    pass

            now = time.monotonic()

            # Simulate elevator movement once every 500 ms.
            if now - last_movement >= 0.5:

                if motor_status == MOTOR_MOVING_UP:
                    if current_floor < MAX_FLOOR:
                        current_floor += 1
                        print(
                            f"Position | Floor: {current_floor} | Direction: UP"
                        )

                elif motor_status == MOTOR_MOVING_DOWN:
                    if current_floor > MIN_FLOOR:
                        current_floor -= 1
                        print(
                            f"Position | Floor: {current_floor} | Direction: DOWN"
                        )

                last_movement = now

            # Periodic position messages.
            if now - last_transmission >= TRANSMISSION_PERIOD:

                send_current_floor(sock, current_floor)
                send_position_status(sock, POSITION_VALID)

                last_transmission = now

            # Periodic heartbeat.
            if now - last_heartbeat >= HEARTBEAT_PERIOD:

                send_heartbeat(sock, heartbeat_counter)
                heartbeat_counter = (heartbeat_counter + 1) % 256

                last_heartbeat = now

    except KeyboardInterrupt:
        print("\nPosition/Sensor ECU stopped.")

    finally:
        sock.close()


if __name__ == "__main__":
    main()
