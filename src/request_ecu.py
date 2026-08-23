import threading
import time

from src.can_utils import (
    create_can_socket,
    send_message,
    encode_uint8,
)


FLOOR_REQUEST_ID = 0x100
HEARTBEAT_ID = 0x110

MIN_FLOOR = 1
MAX_FLOOR = 5

HEARTBEAT_PERIOD = 0.2


def send_floor_request(sock, floor):
    send_message(
        sock,
        FLOOR_REQUEST_ID,
        encode_uint8(floor)
    )

    print(
        f"Floor Request | ID: 0x{FLOOR_REQUEST_ID:03X} | Floor: {floor}"
    )


def request_loop(sock):
    while True:
        user_input = input(
            "Enter destination floor (1-5): "
        )

        try:
            floor = int(user_input)
        except ValueError:
            print("Invalid input. Enter a number from 1 to 5.")
            continue

        if not MIN_FLOOR <= floor <= MAX_FLOOR:
            print("Invalid floor. Valid floors are 1 to 5.")
            continue

        send_floor_request(sock, floor)


def main():
    sock = create_can_socket()

    heartbeat_counter = 0

    print("--------------------------------")
    print("      Passenger Request ECU")
    print("--------------------------------")
    print("SocketCAN interface: vcan0")
    print("Valid floors: 1 - 5")
    print("--------------------------------")

    request_thread = threading.Thread(
        target=request_loop,
        args=(sock,),
        daemon=True
    )

    request_thread.start()

    try:
        while True:
            send_message(
                sock,
                HEARTBEAT_ID,
                encode_uint8(heartbeat_counter)
            )

            heartbeat_counter = (
                heartbeat_counter + 1
            ) % 256

            time.sleep(HEARTBEAT_PERIOD)

    except KeyboardInterrupt:
        print("\nPassenger Request ECU stopped.")

    finally:
        sock.close()


if __name__ == "__main__":
    main()
