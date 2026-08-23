import select
import time

from src.can_utils import (
    create_can_socket,
    send_message,
    receive_message,
    encode_uint8,
    decode_uint8,
)


DOOR_COMMAND_ID = 0x201
DOOR_STATUS_ID = 0x104
HEARTBEAT_ID = 0x114

DOOR_CLOSED = 0
DOOR_OPEN = 1
DOOR_OPENING = 2
DOOR_CLOSING = 3

STATUS_PERIOD = 0.1
HEARTBEAT_PERIOD = 0.2

DOOR_MOVEMENT_TIME = 1.0


def send_door_status(sock, status):
    send_message(
        sock,
        DOOR_STATUS_ID,
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

    door_status = DOOR_CLOSED
    target_status = DOOR_CLOSED

    heartbeat_counter = 0

    last_status = time.monotonic()
    last_heartbeat = time.monotonic()
    movement_start = None

    print("--------------------------------")
    print("            Door ECU")
    print("--------------------------------")
    print("SocketCAN interface: vcan0")
    print("Initial state: CLOSED")
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

                    if can_id == DOOR_COMMAND_ID and data:

                        command = decode_uint8(data)

                        if command == 1:
                            if door_status == DOOR_CLOSED:
                                target_status = DOOR_OPEN
                                door_status = DOOR_OPENING
                                movement_start = time.monotonic()

                                print("Door Command | OPEN")

                        elif command == 0:
                            if door_status == DOOR_OPEN:
                                target_status = DOOR_CLOSED
                                door_status = DOOR_CLOSING
                                movement_start = time.monotonic()

                                print("Door Command | CLOSE")

                        else:
                            print(
                                f"Invalid Door Command: {command}"
                            )

                except BlockingIOError:
                    pass

            now = time.monotonic()

            # Complete door movement after configured movement time.
            if movement_start is not None:

                if now - movement_start >= DOOR_MOVEMENT_TIME:

                    if target_status == DOOR_OPEN:
                        door_status = DOOR_OPEN

                        print("Door Status | OPEN")

                    elif target_status == DOOR_CLOSED:
                        door_status = DOOR_CLOSED

                        print("Door Status | CLOSED")

                    movement_start = None

            # Periodic door status.
            if now - last_status >= STATUS_PERIOD:

                send_door_status(
                    sock,
                    door_status
                )

                last_status = now

            # Periodic heartbeat.
            if now - last_heartbeat >= HEARTBEAT_PERIOD:

                send_heartbeat(
                    sock,
                    heartbeat_counter
                )

                heartbeat_counter = (
                    heartbeat_counter + 1
                ) % 256

                last_heartbeat = now

            time.sleep(0.005)

    except KeyboardInterrupt:
        print("\nDoor ECU stopped.")

    finally:
        send_door_status(
            sock,
            DOOR_CLOSED
        )

        sock.close()


if __name__ == "__main__":
    main()
