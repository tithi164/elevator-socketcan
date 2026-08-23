import os
import select
import time

from src.can_utils import (
    create_can_socket,
    receive_message,
    decode_uint8,
    decode_uint16,
)


CURRENT_FLOOR_ID = 0x101
POSITION_STATUS_ID = 0x102
MOTOR_STATUS_ID = 0x103
DOOR_STATUS_ID = 0x104
FLOOR_REQUEST_ID = 0x100

REQUEST_HEARTBEAT_ID = 0x110
POSITION_HEARTBEAT_ID = 0x111
CONTROLLER_HEARTBEAT_ID = 0x112
MOTOR_HEARTBEAT_ID = 0x113
DOOR_HEARTBEAT_ID = 0x114

CONTROLLER_STATUS_ID = 0x202
FAULT_STATUS_ID = 0x301


HEARTBEAT_TIMEOUT = 0.6


MOTOR_NAMES = {
    0: "STOPPED",
    1: "MOVING_UP",
    2: "MOVING_DOWN",
}


DOOR_NAMES = {
    0: "CLOSED",
    1: "OPEN",
    2: "OPENING",
    3: "CLOSING",
}


CONTROLLER_NAMES = {
    0: "IDLE",
    1: "MOVING_UP",
    2: "MOVING_DOWN",
    3: "DOOR_OPENING",
    4: "DOOR_OPEN",
    5: "DOOR_CLOSING",
    6: "ARRIVED",
    7: "SAFE",
}


POSITION_NAMES = {
    0: "UNKNOWN",
    1: "VALID",
    2: "INVALID",
    3: "SENSOR_FAULT",
}


ECU_NAMES = {
    REQUEST_HEARTBEAT_ID: "Passenger Request",
    POSITION_HEARTBEAT_ID: "Position/Sensor",
    CONTROLLER_HEARTBEAT_ID: "Controller",
    MOTOR_HEARTBEAT_ID: "Motor",
    DOOR_HEARTBEAT_ID: "Door",
}


FAULT_NAMES = {
    0x0000: "NONE",
    0x0001: "HEARTBEAT TIMEOUT",
    0x0002: "INVALID POSITION",
    0x0003: "DOOR FAULT",
    0x0004: "MOTOR FAULT",
    0x0005: "ECU FAILURE",
    0x0006: "RECOVERY DETECTED",
}


def clear_screen():
    os.system("clear")


def print_dashboard(
    current_floor,
    requested_floor,
    position_status,
    motor_status,
    door_status,
    controller_status,
    ecu_last_seen,
    fault_code,
    last_event,
):
    clear_screen()

    print("=" * 56)
    print("              ELEVATOR SYSTEM HMI")
    print("=" * 56)

    print()
    print("SYSTEM STATUS")
    print("-" * 56)

    print(
        f"Current Floor       : {current_floor}"
    )

    requested = (
        str(requested_floor)
        if requested_floor is not None
        else "-"
    )

    print(
        f"Requested Floor     : {requested}"
    )

    print(
        f"Controller State    : "
        f"{CONTROLLER_NAMES.get(controller_status, 'UNKNOWN')}"
    )

    print(
        f"Position Status     : "
        f"{POSITION_NAMES.get(position_status, 'UNKNOWN')}"
    )

    print()
    print("ACTUATORS")
    print("-" * 56)

    print(
        f"Motor Status        : "
        f"{MOTOR_NAMES.get(motor_status, 'UNKNOWN')}"
    )

    print(
        f"Door Status         : "
        f"{DOOR_NAMES.get(door_status, 'UNKNOWN')}"
    )

    print()
    print("ECU STATUS")
    print("-" * 56)

    now = time.monotonic()

    for can_id, name in ECU_NAMES.items():

        last_seen = ecu_last_seen.get(can_id)

        if last_seen is None:
            status = "OFFLINE"

        elif now - last_seen <= HEARTBEAT_TIMEOUT:
            status = "ONLINE"

        else:
            status = "OFFLINE"

        print(
            f"{name:<20}: {status}"
        )

    print()
    print("DIAGNOSTICS")
    print("-" * 56)

    print(
        f"System Fault        : "
        f"{FAULT_NAMES.get(fault_code, 'UNKNOWN FAULT')}"
    )

    print(
        f"Last Event          : {last_event}"
    )

    print()
    print("=" * 56)
    print("SocketCAN interface: vcan0")
    print("=" * 56)


def main():
    sock = create_can_socket()
    sock.setblocking(False)

    current_floor = 1
    requested_floor = None

    position_status = 0
    motor_status = 0
    door_status = 0
    controller_status = 0

    fault_code = 0
    last_event = "-"

    ecu_last_seen = {}

    print_dashboard(
        current_floor,
        requested_floor,
        position_status,
        motor_status,
        door_status,
        controller_status,
        ecu_last_seen,
        fault_code,
        last_event,
    )

    try:
        while True:

            readable, _, _ = select.select(
                [sock],
                [],
                [],
                0.1
            )

            if readable:

                try:
                    can_id, data = receive_message(sock)

                    if not data:
                        continue

                    if can_id == CURRENT_FLOOR_ID:
                        current_floor = decode_uint8(data)

                    elif can_id == POSITION_STATUS_ID:
                        position_status = decode_uint8(data)

                    elif can_id == MOTOR_STATUS_ID:
                        motor_status = decode_uint8(data)

                    elif can_id == DOOR_STATUS_ID:
                        door_status = decode_uint8(data)

                    elif can_id == CONTROLLER_STATUS_ID:
                        controller_status = decode_uint8(data)

                    elif can_id == FAULT_STATUS_ID:
                        fault_code = decode_uint16(data)
                    
                    elif can_id == FLOOR_REQUEST_ID:
                        requested_floor = decode_uint8(data)

                        if fault_code == 0x0006:
                            last_event = "ECU recovery detected"
                        elif fault_code != 0:
                            last_event = (
                                FAULT_NAMES.get(
                                    fault_code,
                                    "Unknown fault"
                                )
                            )
                        else:
                            last_event = "System normal"

                    elif can_id in ECU_NAMES:
                        ecu_last_seen[can_id] = (
                            time.monotonic()
                        )

                except BlockingIOError:
                    pass

            print_dashboard(
                current_floor,
                requested_floor,
                position_status,
                motor_status,
                door_status,
                controller_status,
                ecu_last_seen,
                fault_code,
                last_event,
            )

    except KeyboardInterrupt:
        print("\nHMI stopped.")

    finally:
        sock.close()


if __name__ == "__main__":
    main()
