import select
import time

from src.can_utils import (
    create_can_socket,
    send_message,
    receive_message,
    encode_uint8,
    decode_uint8,
)


MOTOR_COMMAND_ID = 0x200
MOTOR_STATUS_ID = 0x103
HEARTBEAT_ID = 0x113

MOTOR_STOP = 0
MOTOR_UP = 1
MOTOR_DOWN = 2

MIN_FLOOR = 1
MAX_FLOOR = 5

STATUS_PERIOD = 0.1
HEARTBEAT_PERIOD = 0.2


def send_motor_status(sock, status):
    send_message(
        sock,
        MOTOR_STATUS_ID,
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

    motor_status = MOTOR_STOP
    heartbeat_counter = 0

    last_status = time.monotonic()
    last_heartbeat = time.monotonic()

    print("--------------------------------")
    print("           Motor ECU")
    print("--------------------------------")
    print("SocketCAN interface: vcan0")
    print("Initial state: STOPPED")
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

                    if can_id == MOTOR_COMMAND_ID and data:

                        command = decode_uint8(data)

                        if command == MOTOR_STOP:
                            motor_status = MOTOR_STOP
                            print("Motor Command | STOP")

                        elif command == MOTOR_UP:
                            motor_status = MOTOR_UP
                            print("Motor Command | UP")

                        elif command == MOTOR_DOWN:
                            motor_status = MOTOR_DOWN
                            print("Motor Command | DOWN")

                        else:
                            print(
                                f"Invalid Motor Command: {command}"
                            )

                except BlockingIOError:
                    pass

            now = time.monotonic()

            # Periodic motor status
            if now - last_status >= STATUS_PERIOD:

                send_motor_status(
                    sock,
                    motor_status
                )

                last_status = now

            # Periodic heartbeat
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
        print("\nMotor ECU stopped.")

    finally:
        send_motor_status(
            sock,
            MOTOR_STOP
        )

        sock.close()


if __name__ == "__main__":
    main()
