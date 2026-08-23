# CAN Matrix

## 1. Overview

The elevator control system uses SocketCAN on the `vcan0` interface for communication between six independent software ECUs.

Each ECU has a defined CAN message ownership and communication responsibility.

The CAN network contains periodic status and heartbeat messages as well as event-triggered commands.

---

## 2. CAN Message Matrix

| CAN ID | Transmitter | Receiver | Signal / Purpose | Type | Period |
|---|---|---|---|---|---|
| `0x100` | Passenger Request ECU | Controller ECU | Floor Request | Event-triggered | On request |
| `0x101` | Position/Sensor ECU | Controller ECU / HMI | Current Floor | Periodic | 100 ms |
| `0x102` | Position/Sensor ECU | Diagnostic ECU / HMI | Position Status | Periodic | 100 ms |
| `0x103` | Motor ECU | Controller ECU / HMI | Motor Status | Periodic | 100 ms |
| `0x104` | Door ECU | Controller ECU / HMI | Door Status | Periodic | 100 ms |
| `0x110` | Passenger Request ECU | Diagnostic ECU | Heartbeat | Periodic | 200 ms |
| `0x111` | Position/Sensor ECU | Diagnostic ECU | Heartbeat | Periodic | 200 ms |
| `0x112` | Controller ECU | Diagnostic ECU | Heartbeat | Periodic | 200 ms |
| `0x113` | Motor ECU | Diagnostic ECU | Heartbeat | Periodic | 200 ms |
| `0x114` | Door ECU | Diagnostic ECU | Heartbeat | Periodic | 200 ms |
| `0x200` | Controller ECU | Motor ECU | Motor Command | Event-triggered | On command |
| `0x201` | Controller ECU | Door ECU | Door Command | Event-triggered | On command |
| `0x202` | Controller ECU | HMI | Controller Status | Periodic | 200 ms |
| `0x300` | Diagnostic ECU | Controller ECU | Safety Command | Event-triggered | On fault/recovery |
| `0x301` | Diagnostic ECU | HMI | Fault Status | Event-triggered | On diagnostic event |

---

## 3. Periodic Messages

The system uses periodic CAN communication for continuously changing system information and ECU supervision.

### Position and Status Messages

- `0x101` — Current Floor
- `0x102` — Position Status
- `0x103` — Motor Status
- `0x104` — Door Status

These messages are transmitted approximately every 100 ms.

### Heartbeat Messages

- `0x110` — Passenger Request ECU heartbeat
- `0x111` — Position/Sensor ECU heartbeat
- `0x112` — Controller ECU heartbeat
- `0x113` — Motor ECU heartbeat
- `0x114` — Door ECU heartbeat

Heartbeat messages are transmitted approximately every 200 ms.

The Diagnostic ECU uses these messages to detect ECU communication loss.

### Controller Status

`0x202` provides the current Controller ECU state to the HMI.

It is transmitted periodically at approximately 200 ms.

---

## 4. Event-Triggered Messages

The following messages are generated in response to system events.

### Floor Request

`0x100`

Transmitted by the Passenger Request ECU when the user enters a destination floor.

### Motor Command

`0x200`

Transmitted by the Controller ECU when the motor must:

- Stop
- Move upward
- Move downward

### Door Command

`0x201`

Transmitted by the Controller ECU when the door must:

- Open
- Close

### Safety Command

`0x300`

Transmitted by the Diagnostic ECU when:

- A monitored ECU fails
- An invalid sensor value is detected
- A fault is recovered

The command can request:

- Normal operation
- Safety stop
- Emergency stop

### Fault Status

`0x301`

Transmitted by the Diagnostic ECU when a diagnostic fault or recovery event occurs.

---

## 5. CAN Communication Architecture

The communication flow is distributed across the ECUs.

```text
                    +----------------------+
                    | Passenger Request ECU|
                    +----------+-----------+
                               |
                             0x100
                               |
                               v
                    +----------------------+
                    |    Controller ECU    |
                    +----------+-----------+
                         |            |
                    0x200|            |0x201
                         v            v
              +----------------+  +----------------+
              |   Motor ECU    |  |    Door ECU    |
              +----------------+  +----------------+
                       ^
                       |
                 0x101 / 0x102
                       |
              +----------------------+
              | Position/Sensor ECU  |
              +----------------------+

              Diagnostic monitoring:

       0x110  0x111  0x112  0x113  0x114
          \      |      |      |      /
           \     |      |      |     /
            +----------------------+
            |   Diagnostic ECU     |
            +----------+-----------+
                       |
                 0x300 / 0x301
                       |
                       v
              Controller / HMI
              
6. Message Ownership

Each CAN message has a single transmitting ECU.

This provides clear message ownership and prevents multiple ECUs from independently controlling the same function.

ECU	Owned CAN Messages
Passenger Request ECU	0x100, 0x110
Position/Sensor ECU	0x101, 0x102, 0x111
Controller ECU	0x200, 0x201, 0x202, 0x112
Motor ECU	0x103, 0x113
Door ECU	0x104, 0x114
Diagnostic ECU	0x300, 0x301
7. Diagnostic Communication

The Diagnostic ECU monitors the heartbeat messages from the five monitored ECUs.

A heartbeat timeout indicates possible communication loss or ECU failure.

The Diagnostic ECU can then:

Record the fault.
Report the fault.
Request a safety stop.
Monitor for ECU recovery.
Restore normal operation when the fault is cleared.

This provides distributed fault monitoring without requiring the Controller ECU to supervise every ECU directly.

8. CAN Network Requirements Verification

The implementation satisfies the minimum CAN message requirement.

Unique CAN messages: 15
Minimum required: 8
Periodic messages: more than 2
Event-triggered messages: more than 2

Therefore, the CAN network design satisfies the assignment requirements.

9. SocketCAN Interface

All ECUs communicate through the Linux SocketCAN interface:

vcan0

The system is software-only and does not require physical CAN hardware.

CAN traffic can be observed using:

candump vcan0

This allows verification of actual communication between the distributed ECUs.
