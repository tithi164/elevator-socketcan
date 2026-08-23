import select
import time
import os

from src.can_utils import (
    create_can_socket,
    send_message,
    receive_message,
    encode_uint8,
    encode_uint16,
    decode_uint8,
    timestamp,
)


# ============================================================
# CAN IDs
# ============================================================

HEARTBEATS = {
    0x110: "Passenger Request ECU",
    0x111: "Position/Sensor ECU",
    0x112: "Controller ECU",
    0x113: "Motor ECU",
    0x114: "Door ECU",
}

POSITION_STATUS_ID = 0x102
MOTOR_STATUS_ID = 0x103
DOOR_STATUS_ID = 0x104

SAFETY_COMMAND_ID = 0x300
FAULT_STATUS_ID = 0x301


# ============================================================
# Safety Commands
# ============================================================

SAFETY_NORMAL = 0
SAFETY_STOP = 1
SAFETY_EMERGENCY = 2


# ============================================================
# Fault Codes
# ============================================================

FAULT_NONE = 0x0000
FAULT_HEARTBEAT_TIMEOUT = 0x0001
FAULT_INVALID_POSITION = 0x0002
FAULT_DOOR = 0x0003
FAULT_MOTOR = 0x0004
FAULT_ECU_FAILURE = 0x0005
FAULT_RECOVERY = 0x0006


# ============================================================
# Timing
# ============================================================

HEARTBEAT_TIMEOUT = 1.0
STARTUP_GRACE_PERIOD = 2.0
MONITOR_PERIOD = 0.05


# ============================================================
# Logging
# ============================================================

LOG_DIRECTORY = "logs"

LOG_FILE = os.path.join(
    LOG_DIRECTORY,
    "diagnostic.log"
)


def log_event(message):
    os.makedirs(
        LOG_DIRECTORY,
        exist_ok=True
    )

    line = f"{timestamp()} | {message}"

    print(line)

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as log_file:
        log_file.write(line + "\n")


# ============================================================
# CAN Transmission
# ============================================================

def send_safety_command(sock, command):
    send_message(
        sock,
        SAFETY_COMMAND_ID,
        encode_uint8(command)
    )


def send_fault_status(sock, fault_code):
    send_message(
        sock,
        FAULT_STATUS_ID,
        encode_uint16(fault_code)
    )


# ============================================================
# Diagnostic ECU
# ============================================================

def main():

    sock = create_can_socket()
    sock.setblocking(False)

    start_time = time.monotonic()

    # --------------------------------------------------------
    # Last heartbeat received from each ECU
    # --------------------------------------------------------

    last_heartbeat = {
        can_id: start_time
        for can_id in HEARTBEATS
    }

    # --------------------------------------------------------
    # Current failure state of each ECU
    # --------------------------------------------------------

    ecu_failed = {
        can_id: False
        for can_id in HEARTBEATS
    }

    # --------------------------------------------------------
    # Active faults
    # --------------------------------------------------------

    active_faults = set()

    # --------------------------------------------------------
    # Track invalid position fault separately
    # --------------------------------------------------------

    invalid_position_active = False

    print("--------------------------------")
    print("        Diagnostic ECU")
    print("--------------------------------")
    print("SocketCAN interface: vcan0")
    print("Heartbeat timeout: 1000 ms")
    print("Startup grace period: 2 s")
    print("--------------------------------")

    log_event(
        "Diagnostic ECU started"
    )

    try:

        while True:

            # =================================================
            # Wait for CAN traffic
            # =================================================

            readable, _, _ = select.select(
                [sock],
                [],
                [],
                MONITOR_PERIOD
            )

            # =================================================
            # Drain ALL currently queued CAN messages
            # =================================================

            if readable:

                while True:

                    try:

                        can_id, data = receive_message(sock)

                        if not data:
                            continue

                        # -------------------------------------
                        # Heartbeat
                        # -------------------------------------

                        if can_id in HEARTBEATS:

                            was_failed = ecu_failed[can_id]

                            last_heartbeat[can_id] = (
                                time.monotonic()
                            )

                            # ECU has recovered.
                            if was_failed:

                                ecu_failed[can_id] = False

                                fault_key = (
                                    FAULT_HEARTBEAT_TIMEOUT,
                                    can_id
                                )

                                active_faults.discard(
                                    fault_key
                                )

                                log_event(
                                    f"RECOVERY: "
                                    f"{HEARTBEATS[can_id]} "
                                    f"heartbeat restored"
                                )

                                send_fault_status(
                                    sock,
                                    FAULT_RECOVERY
                                )

                                # If there are no remaining
                                # faults, restore normal operation.
                                if not active_faults:

                                    send_safety_command(
                                        sock,
                                        SAFETY_NORMAL
                                    )

                                    send_fault_status(
                                        sock,
                                        FAULT_NONE
                                    )

                                    log_event(
                                        "SYSTEM RECOVERY: "
                                        "All monitored ECUs "
                                        "operational"
                                    )

                        # -------------------------------------
                        # Position Status
                        # -------------------------------------

                        elif can_id == POSITION_STATUS_ID:

                            value = decode_uint8(data)

                            valid_position = value in (
                                0,
                                1,
                                2,
                                3
                            )

                            # =================================
                            # Invalid position detected
                            # =================================

                            if not valid_position:

                                if not invalid_position_active:

                                    invalid_position_active = True

                                    active_faults.add(
                                        FAULT_INVALID_POSITION
                                    )

                                    log_event(
                                        "FAULT: Invalid "
                                        "position status"
                                    )

                                    send_fault_status(
                                        sock,
                                        FAULT_INVALID_POSITION
                                    )

                                    send_safety_command(
                                        sock,
                                        SAFETY_STOP
                                    )

                            # =================================
                            # Invalid position recovered
                            # =================================

                            else:

                                if invalid_position_active:

                                    invalid_position_active = False

                                    active_faults.discard(
                                        FAULT_INVALID_POSITION
                                    )

                                    log_event(
                                        "RECOVERY: Invalid "
                                        "position status restored"
                                    )

                                    send_fault_status(
                                        sock,
                                        FAULT_RECOVERY
                                    )

                                    # If there are no remaining
                                    # faults, return to normal.
                                    if not active_faults:

                                        send_safety_command(
                                            sock,
                                            SAFETY_NORMAL
                                        )

                                        send_fault_status(
                                            sock,
                                            FAULT_NONE
                                        )

                                        log_event(
                                            "SYSTEM RECOVERY: "
                                            "All monitored systems "
                                            "operational"
                                        )

                        # -------------------------------------
                        # Motor Status
                        # -------------------------------------

                        elif can_id == MOTOR_STATUS_ID:

                            value = decode_uint8(data)

                            if value not in (
                                0,
                                1,
                                2
                            ):

                                if (
                                    FAULT_MOTOR
                                    not in active_faults
                                ):

                                    active_faults.add(
                                        FAULT_MOTOR
                                    )

                                    log_event(
                                        "FAULT: Invalid "
                                        "motor status"
                                    )

                                    send_fault_status(
                                        sock,
                                        FAULT_MOTOR
                                    )

                                    send_safety_command(
                                        sock,
                                        SAFETY_STOP
                                    )

                        # -------------------------------------
                        # Door Status
                        # -------------------------------------

                        elif can_id == DOOR_STATUS_ID:

                            value = decode_uint8(data)

                            if value not in (
                                0,
                                1,
                                2,
                                3
                            ):

                                if (
                                    FAULT_DOOR
                                    not in active_faults
                                ):

                                    active_faults.add(
                                        FAULT_DOOR
                                    )

                                    log_event(
                                        "FAULT: Invalid "
                                        "door status"
                                    )

                                    send_fault_status(
                                        sock,
                                        FAULT_DOOR
                                    )

                                    send_safety_command(
                                        sock,
                                        SAFETY_STOP
                                    )

                    except BlockingIOError:

                        # No more CAN frames waiting.
                        break

            # =================================================
            # Startup Grace Period
            # =================================================

            now = time.monotonic()

            if (
                now - start_time
                < STARTUP_GRACE_PERIOD
            ):

                continue

            # =================================================
            # Heartbeat Timeout Detection
            # =================================================

            for can_id, ecu_name in HEARTBEATS.items():

                elapsed = (
                    now - last_heartbeat[can_id]
                )

                if elapsed > HEARTBEAT_TIMEOUT:

                    if not ecu_failed[can_id]:

                        ecu_failed[can_id] = True

                        fault_key = (
                            FAULT_HEARTBEAT_TIMEOUT,
                            can_id
                        )

                        active_faults.add(
                            fault_key
                        )

                        log_event(
                            f"FAULT: {ecu_name} "
                            f"heartbeat timeout"
                        )

                        send_fault_status(
                            sock,
                            FAULT_HEARTBEAT_TIMEOUT
                        )

                        # A missing ECU causes a safe stop.
                        if can_id != 0x112:

                            send_safety_command(
                                sock,
                                SAFETY_STOP
                            )

            time.sleep(0.005)

    except KeyboardInterrupt:

        print(
            "\nDiagnostic ECU stopped."
        )

        log_event(
            "Diagnostic ECU stopped"
        )

    finally:

        sock.close()


if __name__ == "__main__":
    main()
