# Message Definition

## 1. Overview

This document defines the encoding rules for CAN signals used by the distributed elevator control system.

The encoding strategy is intentionally simple and deterministic so that messages can be encoded and decoded consistently by all independent ECU applications.

Signals use unsigned integer or enumerated-state encoding unless otherwise specified.

## 2. General Encoding Rules

* CAN data bytes use unsigned integer encoding.
* Multi-byte values use big-endian byte order.
* Discrete states are represented using enumerated integer values.
* Reserved or invalid values are explicitly defined where applicable.
* Signal values outside their defined valid range shall be treated as invalid.
* The CAN payload length is determined by the signals contained in the message.

## 3. Floor Request — CAN ID 0x100

### Signal

| Property   | Definition        |
| ---------- | ----------------- |
| Signal     | Destination Floor |
| Size       | 1 byte            |
| Unit       | Floor             |
| Resolution | 1 floor           |
| Range      | 1–5               |
| Encoding   | Unsigned integer  |

### Encoding

```text
0x01 = Floor 1
0x02 = Floor 2
0x03 = Floor 3
0x04 = Floor 4
0x05 = Floor 5
```

`0x00` is reserved as an invalid/uninitialized value.

## 4. Current Floor — CAN ID 0x101

| Property   | Definition       |
| ---------- | ---------------- |
| Signal     | Current Floor    |
| Size       | 1 byte           |
| Unit       | Floor            |
| Resolution | 1 floor          |
| Range      | 1–5              |
| Encoding   | Unsigned integer |

The value represents the current simulated elevator floor.

## 5. Position Status — CAN ID 0x102

| Property   | Definition         |
| ---------- | ------------------ |
| Signal     | Position Status    |
| Size       | 1 byte             |
| Unit       | State              |
| Resolution | 1                  |
| Range      | 0–3                |
| Encoding   | Enumerated integer |

```text
0 = UNKNOWN
1 = VALID
2 = INVALID
3 = SENSOR_FAULT
```

## 6. Motor Status — CAN ID 0x103

| Property   | Definition         |
| ---------- | ------------------ |
| Signal     | Motor Status       |
| Size       | 1 byte             |
| Unit       | State              |
| Resolution | 1                  |
| Range      | 0–2                |
| Encoding   | Enumerated integer |

```text
0 = STOPPED
1 = MOVING_UP
2 = MOVING_DOWN
```

## 7. Door Status — CAN ID 0x104

| Property   | Definition         |
| ---------- | ------------------ |
| Signal     | Door Status        |
| Size       | 1 byte             |
| Unit       | State              |
| Resolution | 1                  |
| Range      | 0–3                |
| Encoding   | Enumerated integer |

```text
0 = CLOSED
1 = OPEN
2 = OPENING
3 = CLOSING
```

## 8. ECU Heartbeat — CAN IDs 0x110–0x114

Each ECU periodically transmits a heartbeat message.

| Property     | Definition        |
| ------------ | ----------------- |
| Signal       | Heartbeat Counter |
| Size         | 1 byte            |
| Unit         | Count             |
| Resolution   | 1                 |
| Range        | 0–255             |
| Encoding     | Unsigned integer  |
| Transmission | Periodic, 200 ms  |

The counter increments for each transmitted heartbeat and wraps from `255` to `0`.

### Heartbeat CAN IDs

| CAN ID  | ECU                   |
| ------- | --------------------- |
| `0x110` | Passenger Request ECU |
| `0x111` | Position/Sensor ECU   |
| `0x112` | Controller ECU        |
| `0x113` | Motor ECU             |
| `0x114` | Door ECU              |

The Diagnostic ECU monitors these messages to detect missing ECU communication.

## 9. Motor Command — CAN ID 0x200

| Property   | Definition         |
| ---------- | ------------------ |
| Signal     | Motor Command      |
| Size       | 1 byte             |
| Unit       | State              |
| Resolution | 1                  |
| Range      | 0–2                |
| Encoding   | Enumerated integer |

```text
0 = STOP
1 = UP
2 = DOWN
```

The Controller ECU transmits this command to the Motor ECU.

## 11. Controller Status — CAN ID 0x202

| Property | Definition |
|---|---|
| Signal | Controller State |
| Size | 1 byte |
| Unit | State |
| Resolution | 1 |
| Range | 0–7 |
| Encoding | Enumerated integer |
| Transmission | Periodic, 200 ms |

### Controller State Encoding

```text
0 = IDLE
1 = MOVING_UP
2 = MOVING_DOWN
3 = DOOR_OPENING
4 = DOOR_OPEN
5 = DOOR_CLOSING
6 = ARRIVED
7 = SAFE

## 10. Door Command — CAN ID 0x201

| Property   | Definition         |
| ---------- | ------------------ |
| Signal     | Door Command       |
| Size       | 1 byte             |
| Unit       | State              |
| Resolution | 1                  |
| Range      | 0–1                |
| Encoding   | Enumerated integer |

```text
0 = CLOSE
1 = OPEN
```

The Controller ECU transmits this command to the Door ECU.

## 11. Safety Command — CAN ID 0x300

| Property   | Definition         |
| ---------- | ------------------ |
| Signal     | Safety Command     |
| Size       | 1 byte             |
| Unit       | State              |
| Resolution | 1                  |
| Range      | 0–2                |
| Encoding   | Enumerated integer |

```text
0 = NORMAL
1 = SAFE_STOP
2 = EMERGENCY_STOP
```

The Diagnostic ECU transmits safety commands to the Controller ECU when a critical fault is detected.

## 12. Fault Status — CAN ID 0x301

| Property   | Definition       |
| ---------- | ---------------- |
| Signal     | Fault Code       |
| Size       | 2 bytes          |
| Unit       | Fault code       |
| Resolution | 1                |
| Range      | 0–65535          |
| Encoding   | Unsigned integer |
| Byte Order | Big-endian       |

### Fault Codes

```text
0x0000 = NO_FAULT
0x0001 = HEARTBEAT_TIMEOUT
0x0002 = INVALID_POSITION
0x0003 = DOOR_FAULT
0x0004 = MOTOR_FAULT
0x0005 = ECU_FAILURE
0x0006 = RECOVERY_DETECTED
```

## 13. Signal Validation

Received signals shall be validated against their defined ranges.

Examples:

```text
Current Floor = 1–5       → Valid
Current Floor = 8         → Invalid

Motor Status = 0–2        → Valid
Motor Status = 7          → Invalid

Door Status = 0–3         → Valid
Door Status = 9           → Invalid
```

Invalid values shall be reported to the Diagnostic ECU and handled according to the system fault-handling strategy.

## 14. Message Encoding Summary

| CAN ID        | Message         | Signal            |    Size | Encoding |
| ------------- | --------------- | ----------------- | ------: | -------- |
| `0x100`       | Floor Request   | Destination Floor |  1 byte | Unsigned |
| `0x101`       | Current Floor   | Current Floor     |  1 byte | Unsigned |
| `0x102`       | Position Status | Position Status   |  1 byte | Enum     |
| `0x103`       | Motor Status    | Motor Status      |  1 byte | Enum     |
| `0x104`       | Door Status     | Door Status       |  1 byte | Enum     |
| `0x110–0x114` | ECU Heartbeat   | Heartbeat Counter |  1 byte | Unsigned |
| `0x200`       | Motor Command   | Motor Command     |  1 byte | Enum     |
| `0x201`       | Door Command    | Door Command      |  1 byte | Enum     |
| `0x300`       | Safety Command  | Safety Command    |  1 byte | Enum     |
| `0x301`       | Fault Status    | Fault Code        | 2 bytes | Unsigned |

## 15. Design Rationale

The message encoding uses simple integer and enumerated representations because the simulated elevator primarily exchanges discrete states and floor information.

This approach provides:

* Simple implementation.
* Deterministic encoding.
* Easy CAN traffic inspection.
* Easy fault injection.
* Clear signal validation.
* Consistent interpretation across independent ECUs.

