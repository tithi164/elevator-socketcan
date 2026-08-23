# Signal Specification

## 1. Overview

This document defines the encoding rules for signals transmitted through the SocketCAN network of the Elevator Control System.

Each signal is mapped to a CAN message and has a defined data type, unit, valid range, resolution, and encoding strategy.

The system uses standard CAN frames with a maximum payload of 8 bytes.

---

## 2. Encoding Strategy

The current implementation uses unsigned integer encoding for the primary elevator signals.

For one-byte signals:

- Data length: 1 byte
- Data type: Unsigned 8-bit integer
- Resolution: 1 unit/bit
- Byte order: Not applicable for single-byte values

For two-byte diagnostic fault codes:

- Data length: 2 bytes
- Data type: Unsigned 16-bit integer
- Resolution: 1 code/bit
- Byte order: Big-endian

Unused CAN payload bytes are padded with zeroes.

---

## 3. Floor Request

### CAN ID

`0x100`

### Transmitter

Passenger Request ECU

### Receiver

Controller ECU

### Signal

Destination Floor

| Parameter | Definition |
|---|---|
| Data Length | 1 byte |
| Data Type | Unsigned 8-bit |
| Unit | Floor number |
| Resolution | 1 floor/bit |
| Valid Range | 1–5 |
| Encoding | Unsigned integer |
| Transmission | Event-triggered |

### Encoding

```text
1 → Floor 1
2 → Floor 2
3 → Floor 3
4 → Floor 4
5 → Floor 5

Values outside the range 1–5 are rejected by the Passenger Request ECU.

4. Current Floor
CAN ID

0x101

Transmitter

Position/Sensor ECU

Receiver

Controller ECU / HMI

Signal

Current Floor

Parameter	Definition
Data Length	1 byte
Data Type	Unsigned 8-bit
Unit	Floor number
Resolution	1 floor/bit
Valid Range	1–5
Encoding	Unsigned integer
Transmission	Periodic
Period	Approximately 100 ms
Encoding
1 → Floor 1
2 → Floor 2
3 → Floor 3
4 → Floor 4
5 → Floor 5
5. Position Status
CAN ID

0x102

Transmitter

Position/Sensor ECU

Receiver

Diagnostic ECU / HMI

Signal

Position Sensor Status

Parameter	Definition
Data Length	1 byte
Data Type	Unsigned 8-bit
Unit	Status code
Resolution	1 status code/bit
Valid Range	0–3
Encoding	Enumerated unsigned integer
Transmission	Periodic
Period	Approximately 100 ms
Status Encoding
Value	Meaning
0	POSITION_UNKNOWN
1	POSITION_VALID
2	POSITION_INVALID
3	POSITION_SENSOR_FAULT

Values outside 0–3 are considered invalid by the Diagnostic ECU.

Example fault injection:

cansend vcan0 102#FF

FF represents decimal 255, which is outside the valid range.

6. Motor Status
CAN ID

0x103

Transmitter

Motor ECU

Receiver

Controller ECU / HMI

Signal

Motor Status

Parameter	Definition
Data Length	1 byte
Data Type	Unsigned 8-bit
Unit	Status code
Resolution	1 status code/bit
Valid Range	0–2
Encoding	Enumerated unsigned integer
Transmission	Periodic
Period	Approximately 100 ms
Status Encoding
Value	Meaning
0	MOTOR_STOP
1	MOTOR_UP
2	MOTOR_DOWN
7. Door Status
CAN ID

0x104

Transmitter

Door ECU

Receiver

Controller ECU / HMI

Signal

Door Status

Parameter	Definition
Data Length	1 byte
Data Type	Unsigned 8-bit
Unit	Status code
Resolution	1 status code/bit
Valid Range	0–3
Encoding	Enumerated unsigned integer
Transmission	Periodic
Period	Approximately 100 ms
Status Encoding
Value	Meaning
0	DOOR_CLOSED
1	DOOR_OPEN
2	DOOR_OPENING
3	DOOR_CLOSING
8. Heartbeat Messages

The system uses dedicated heartbeat CAN IDs for ECU supervision.

Heartbeat CAN IDs
CAN ID	ECU
0x110	Passenger Request ECU
0x111	Position/Sensor ECU
0x112	Controller ECU
0x113	Motor ECU
0x114	Door ECU
Signal Definition
Parameter	Definition
Data Length	1 byte
Data Type	Unsigned 8-bit
Unit	Counter value
Resolution	1 count/bit
Range	0–255
Encoding	Unsigned integer
Transmission	Periodic
Period	Approximately 200 ms
Counter Behavior

The heartbeat counter increments after every transmission:

0 → 1 → 2 → ... → 254 → 255 → 0

The counter is primarily used to demonstrate continued ECU communication.

The Diagnostic ECU primarily determines ECU availability from the arrival time of heartbeat frames.

9. Motor Command
CAN ID

0x200

Transmitter

Controller ECU

Receiver

Motor ECU

Signal

Motor Command

Parameter	Definition
Data Length	1 byte
Data Type	Unsigned 8-bit
Unit	Command code
Resolution	1 command/bit
Valid Range	0–2
Encoding	Enumerated unsigned integer
Transmission	Event-triggered
Command Encoding
Value	Meaning
0	MOTOR_STOP
1	MOTOR_UP
2	MOTOR_DOWN
10. Door Command
CAN ID

0x201

Transmitter

Controller ECU

Receiver

Door ECU

Signal

Door Command

Parameter	Definition
Data Length	1 byte
Data Type	Unsigned 8-bit
Unit	Command code
Resolution	1 command/bit
Valid Range	0–1
Encoding	Enumerated unsigned integer
Transmission	Event-triggered
Command Encoding
Value	Meaning
0	CLOSE
1	OPEN
11. Controller Status
CAN ID

0x202

Transmitter

Controller ECU

Receiver

HMI

Signal

Controller State

Parameter	Definition
Data Length	1 byte
Data Type	Unsigned 8-bit
Unit	State code
Resolution	1 state/bit
Encoding	Enumerated unsigned integer
Transmission	Periodic
Period	Approximately 200 ms
State Encoding
Value	Controller State
0	IDLE
1	MOVING_UP
2	MOVING_DOWN
3	DOOR_OPENING
4	DOOR_OPEN
5	DOOR_CLOSING
6	ARRIVED
7	SAFE
12. Safety Command
CAN ID

0x300

Transmitter

Diagnostic ECU

Receiver

Controller ECU

Signal

Safety Command

Parameter	Definition
Data Length	1 byte
Data Type	Unsigned 8-bit
Unit	Safety command
Resolution	1 command/bit
Valid Range	0–2
Encoding	Enumerated unsigned integer
Transmission	Event-triggered
Command Encoding
Value	Meaning
0	SAFETY_NORMAL
1	SAFETY_STOP
2	SAFETY_EMERGENCY
Behavior

When SAFETY_STOP or SAFETY_EMERGENCY is received, the Controller commands the Motor ECU to stop and places the controller in the SAFE state.

When SAFETY_NORMAL is received after fault recovery, the Controller returns to normal operation.

13. Fault Status
CAN ID

0x301

Transmitter

Diagnostic ECU

Receiver

HMI

Signal

Diagnostic Fault Code

Parameter	Definition
Data Length	2 bytes
Data Type	Unsigned 16-bit
Unit	Fault code
Resolution	1 code/bit
Range	0–65535
Encoding	Unsigned integer
Byte Order	Big-endian
Transmission	Event-triggered
Fault Encoding
Code	Meaning
0x0000	FAULT_NONE
0x0001	FAULT_HEARTBEAT_TIMEOUT
0x0002	FAULT_INVALID_POSITION
0x0003	FAULT_DOOR
0x0004	FAULT_MOTOR
0x0005	FAULT_ECU_FAILURE
0x0006	FAULT_RECOVERY
14. CAN Frame Format

All application messages use standard CAN frames.

The SocketCAN implementation uses:

CAN ID
DLC
DATA[0..7]

The current application signals use one or two data bytes.

Example:

CAN ID: 0x100
DLC:    1
DATA:   05

This represents:

Destination Floor = 5

Another example:

CAN ID: 0x300
DLC:    1
DATA:   01

represents:

SAFETY_STOP
15. Fault Injection Encoding

The implementation supports software-based fault injection through SocketCAN.

For the Position Status signal:

cansend vcan0 102#FF

This generates:

CAN ID = 0x102
Data   = FF

Since 255 is outside the valid position-status range 0–3, the Diagnostic ECU detects an invalid sensor value and requests a safety stop.

This provides a repeatable method for verification of sensor fault handling.

16. Summary

The signal definitions provide:

Clearly defined CAN IDs
Defined message ownership
Explicit signal ranges
Defined encoding strategies
Periodic communication for system status
Event-triggered communication for commands and faults
Heartbeat-based ECU supervision
Software-based fault injection

These definitions form the basis for implementation, diagnostics, verification, and validation of the Elevator Control System.
