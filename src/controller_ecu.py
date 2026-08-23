import select
import time

from src.can_utils import (
    create_can_socket,
    send_message,
    receive_message,
    encode_uint8,
    decode_uint8,
)


FLOOR_REQUEST_ID = 0x100
CURRENT_FLOOR_ID = 0x101
MOTOR_STATUS_ID = 0x103
DOOR_STATUS_ID = 0x104
SAFETY_COMMAND_ID = 0x300

MOTOR_COMMAND_ID = 0x200
DOOR_COMMAND_ID = 0x201
HEARTBEAT_ID = 0x112
CONTROLLER_STATUS_ID = 0x202


MOTOR_STOP = 0
MOTOR_UP = 1
MOTOR_DOWN = 2

DOOR_CLOSED = 0
DOOR_OPEN = 1
DOOR_OPENING = 2
DOOR_CLOSING = 3

SAFETY_NORMAL = 0
SAFETY_STOP = 1
SAFETY_EMERGENCY = 2

STATE_IDLE = "IDLE"
STATE_REQUEST_RECEIVED = "REQUEST_RECEIVED"
STATE_DOOR_CLOSING = "DOOR_CLOSING"
STATE_MOVING_UP = "MOVING_UP"
STATE_MOVING_DOWN = "MOVING_DOWN"
STATE_ARRIVED = "ARRIVED"
STATE_DOOR_OPENING = "DOOR_OPENING"
STATE_DOOR_OPEN = "DOOR_OPEN"
STATE_FAULT = "FAULT"
STATE_SAFE = "SAFE"

HEARTBEAT_PERIOD = 0.2
STATUS_PERIOD = 0.2
DOOR_OPEN_TIME = 1.0


CONTROLLER_STATUS_CODES = {
    STATE_IDLE: 0,
    STATE_MOVING_UP: 1,
    STATE_MOVING_DOWN: 2,
    STATE_DOOR_OPENING: 3,
    STATE_DOOR_OPEN: 4,
    STATE_DOOR_CLOSING: 5,
    STATE_ARRIVED: 6,
    STATE_SAFE: 7,
}


def send_motor_command(sock, command):

    send_message(
        sock,
        MOTOR_COMMAND_ID,
        encode_uint8(command)
    )

    names = {
        MOTOR_STOP: "STOP",
        MOTOR_UP: "UP",
        MOTOR_DOWN: "DOWN",
    }

    print(
        f"Motor Command | ID: 0x{MOTOR_COMMAND_ID:03X} | "
        f"{names.get(command, 'UNKNOWN')}"
    )


def send_door_command(sock, command):

    send_message(
        sock,
        DOOR_COMMAND_ID,
        encode_uint8(command)
    )

    name = "OPEN" if command == 1 else "CLOSE"

    print(
        f"Door Command | ID: 0x{DOOR_COMMAND_ID:03X} | {name}"
    )


def send_controller_status(sock, state):

    status_code = CONTROLLER_STATUS_CODES.get(
        state,
        7
    )

    send_message(
        sock,
        CONTROLLER_STATUS_ID,
        encode_uint8(status_code)
    )


def main():

    sock = create_can_socket()
    sock.setblocking(False)

    current_floor = 1
    target_floor = None

    motor_status = MOTOR_STOP
    door_status = DOOR_CLOSED

    safety_command = SAFETY_NORMAL

    state = STATE_IDLE

    heartbeat_counter = 0
    last_heartbeat = time.monotonic()

    last_status = time.monotonic()

    door_open_start = None

    print("--------------------------------")
    print("         Controller ECU")
    print("--------------------------------")
    print("SocketCAN interface: vcan0")
    print("--------------------------------")

    try:

        while True:

            # =================================================
            # CAN reception
            # =================================================

            readable, _, _ = select.select(
                [sock],
                [],
                [],
                0.02
            )

            if readable:

                try:

                    can_id, data = receive_message(sock)

                    if not data:
                        continue

                    value = decode_uint8(data)

                    # -----------------------------------------
                    # Floor Request
                    # -----------------------------------------

                    if can_id == FLOOR_REQUEST_ID:

                        if 1 <= value <= 5:

                            target_floor = value

                            if state == STATE_IDLE:

                                state = STATE_REQUEST_RECEIVED

                            print(
                                f"Floor Request Received | "
                                f"Target: {target_floor}"
                            )

                    # -----------------------------------------
                    # Current Floor
                    # -----------------------------------------

                    elif can_id == CURRENT_FLOOR_ID:

                        if 1 <= value <= 5:

                            if value != current_floor:

                                print(
                                    f"Current Floor | {value}"
                                )

                            current_floor = value

                    # -----------------------------------------
                    # Motor Status
                    # -----------------------------------------

                    elif can_id == MOTOR_STATUS_ID:

                        motor_status = value

                    # -----------------------------------------
                    # Door Status
                    # -----------------------------------------

                    elif can_id == DOOR_STATUS_ID:

                        door_status = value

                    # -----------------------------------------
                    # Safety Command
                    # -----------------------------------------

                    elif can_id == SAFETY_COMMAND_ID:

                        safety_command = value

                        if value in (
                            SAFETY_STOP,
                            SAFETY_EMERGENCY
                        ):

                            send_motor_command(
                                sock,
                                MOTOR_STOP
                            )

                            state = STATE_SAFE

                            print(
                                "SAFETY COMMAND RECEIVED "
                                "-> MOTOR STOP"
                            )

                        elif value == SAFETY_NORMAL:

                            print(
                                "SAFETY RECOVERY RECEIVED "
                                "-> NORMAL OPERATION"
                            )

                            safety_command = SAFETY_NORMAL

                            if state == STATE_SAFE:

                                state = STATE_IDLE

                                target_floor = None

                except BlockingIOError:

                    pass

            # =================================================
            # Safety handling
            # =================================================

            if safety_command != SAFETY_NORMAL:

                if motor_status != MOTOR_STOP:

                    send_motor_command(
                        sock,
                        MOTOR_STOP
                    )

                state = STATE_SAFE

            # =================================================
            # Normal elevator control
            # =================================================

            elif target_floor is not None:

                if state == STATE_SAFE:

                    pass

                elif state == STATE_REQUEST_RECEIVED:

                    if current_floor == target_floor:

                        state = STATE_ARRIVED

                    elif door_status != DOOR_CLOSED:

                        send_door_command(
                            sock,
                            0
                        )

                        state = STATE_DOOR_CLOSING

                    else:

                        if target_floor > current_floor:

                            send_motor_command(
                                sock,
                                MOTOR_UP
                            )

                            state = STATE_MOVING_UP

                        elif target_floor < current_floor:

                            send_motor_command(
                                sock,
                                MOTOR_DOWN
                            )

                            state = STATE_MOVING_DOWN

                elif state == STATE_DOOR_CLOSING:

                    if door_status == DOOR_CLOSED:

                        if target_floor > current_floor:

                            send_motor_command(
                                sock,
                                MOTOR_UP
                            )

                            state = STATE_MOVING_UP

                        elif target_floor < current_floor:

                            send_motor_command(
                                sock,
                                MOTOR_DOWN
                            )

                            state = STATE_MOVING_DOWN

                elif state in (
                    STATE_MOVING_UP,
                    STATE_MOVING_DOWN
                ):

                    if current_floor == target_floor:

                        send_motor_command(
                            sock,
                            MOTOR_STOP
                        )

                        state = STATE_ARRIVED

                elif state == STATE_ARRIVED:

                    send_door_command(
                        sock,
                        1
                    )

                    state = STATE_DOOR_OPENING

                elif state == STATE_DOOR_OPENING:

                    if door_status == DOOR_OPEN:

                        state = STATE_DOOR_OPEN

                        door_open_start = time.monotonic()

                elif state == STATE_DOOR_OPEN:

                    # -----------------------------------------
                    # Non-blocking door-open delay.
                    # Controller continues sending heartbeat.
                    # -----------------------------------------

                    if (
                        door_open_start is not None
                        and
                        time.monotonic() - door_open_start
                        >= DOOR_OPEN_TIME
                    ):

                        send_door_command(
                            sock,
                            0
                        )

                        target_floor = None
                        door_open_start = None
                        state = STATE_IDLE

            # =================================================
            # Periodic heartbeat
            # =================================================

            now = time.monotonic()

            if now - last_heartbeat >= HEARTBEAT_PERIOD:

                send_message(
                    sock,
                    HEARTBEAT_ID,
                    encode_uint8(
                        heartbeat_counter
                    )
                )

                heartbeat_counter = (
                    heartbeat_counter + 1
                ) % 256

                last_heartbeat = now

            # =================================================
            # Periodic controller status
            # =================================================

            now = time.monotonic()

            if now - last_status >= STATUS_PERIOD:

                send_controller_status(
                    sock,
                    state
                )

                last_status = now

            time.sleep(0.005)

    except KeyboardInterrupt:

        print(
            "\nController ECU stopped."
        )

    finally:

        send_motor_command(
            sock,
            MOTOR_STOP
        )

        sock.close()


if __name__ == "__main__":
    main()
