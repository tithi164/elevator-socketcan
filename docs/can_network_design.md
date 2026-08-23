# CAN Network Design

## 1. Overview

The elevator system uses Linux SocketCAN and the virtual CAN interface `vcan0` as the communication network between independent software ECUs.

The CAN network provides communication for floor requests, position feedback, motor status, door status, ECU heartbeat monitoring, actuator commands, and diagnostic/safety information.

## 2. CAN ID Allocation

The CAN identifiers are organized into functional ranges:

| CAN ID Range  | Purpose                           |
| ------------- | --------------------------------- |
| `0x100–0x1FF` | System status and sensor messages |
| `0x200–0x2FF` | Control commands                  |
| `0x300–0x3FF` | Diagnostics and safety            |

## 3. CAN Matrix

| CAN ID  | Transmitter           | Receiver       | Signal / Message | Type            | Transmission Rate |
| ------- | --------------------- | -------------- | ---------------- | --------------- | ----------------- |
| `0x100` | Passenger Request ECU | Controller ECU | Floor Request    | Event-triggered | On request        |
| `0x101` | Position/Sensor ECU   | Controller ECU | Current Floor    | Periodic        | 100 ms            |
| `0x102` | Position/Sensor ECU   | Diagnostic ECU | Position Status  | Periodic        | 100 ms            |
| `0x103` | Motor ECU             | Controller ECU | Motor Status     | Periodic        | 100 ms            |
| `0x104` | Door ECU              | Controller ECU | Door Status      | Periodic        | 100 ms            |
| `0x110` | Passenger Request ECU | Diagnostic ECU | ECU Heartbeat    | Periodic        | 200 ms            |
| `0x111` | Position/Sensor ECU   | Diagnostic ECU | ECU Heartbeat    | Periodic        | 200 ms            |
| `0x112` | Controller ECU        | Diagnostic ECU | ECU Heartbeat    | Periodic        | 200 ms            |
| `0x113` | Motor ECU             | Diagnostic ECU | ECU Heartbeat    | Periodic        | 200 ms            |
| `0x114` | Door ECU              | Diagnostic ECU | ECU Heartbeat    | Periodic        | 200 ms            |
| `0x200` | Controller ECU        | Motor ECU      | Motor Command    | Event-triggered | On change         |
| `0x201` | Controller ECU        | Door ECU       | Door Command     | Event-triggered | On change         |
| `0x300` | Diagnostic ECU        | Controller ECU | Safety Command   | Event-triggered | On fault          |
| `0x301` | Diagnostic ECU        | HMI            | Fault Status     | Event-triggered | On change         |

## 4. CAN Message Ownership

### Passenger Request ECU

The Passenger Request ECU owns:

* `0x100` — Floor Request
* `0x110` — Passenger Request ECU Heartbeat

### Position/Sensor ECU

The Position/Sensor ECU owns:

* `0x101` — Current Floor
* `0x102` — Position Status
* `0x111` — Position/Sensor ECU Heartbeat

### Controller ECU

The Controller ECU owns:

* `0x112` — Controller ECU Heartbeat
* `0x200` — Motor Command
* `0x201` — Door Command

### Motor ECU

The Motor ECU owns:

* `0x103` — Motor Status
* `0x113` — Motor ECU Heartbeat

### Door ECU

The Door ECU owns:

* `0x104` — Door Status
* `0x114` — Door ECU Heartbeat

### Diagnostic ECU

The Diagnostic ECU owns:

* `0x300` — Safety Command
* `0x301` — Fault Status

## 5. Periodic Messages

Periodic messages are transmitted at defined intervals without requiring a new external event.

The system uses periodic messages for:

* Current floor
* Position status
* Motor status
* Door status
* ECU heartbeats

Periodic messages are important for system monitoring because the Diagnostic ECU can detect a missing message or heartbeat when an expected transmission does not arrive within the configured timeout.

## 6. Event-Triggered Messages

Event-triggered messages are transmitted when a system event occurs.

The system uses event-triggered messages for:

* Floor requests
* Motor commands
* Door commands
* Safety commands
* Fault status changes

## 7. Communication Flow

### Floor Request

```text
Passenger
   |
   v
Passenger Request ECU
   |
   | 0x100 Floor Request
   v
Controller ECU
```

### Position Feedback

```text
Position/Sensor ECU
   |
   | 0x101 Current Floor
   v
Controller ECU
```

### Motor Control

```text
Controller ECU
   |
   | 0x200 Motor Command
   v
Motor ECU
   |
   | 0x103 Motor Status
   v
Controller ECU
```

### Door Control

```text
Controller ECU
   |
   | 0x201 Door Command
   v
Door ECU
   |
   | 0x104 Door Status
   v
Controller ECU
```

### Diagnostic Monitoring

```text
All monitored ECUs
       |
       | Heartbeats / Status
       v
Diagnostic ECU
       |
       | Fault / Safety information
       v
Controller ECU
```

## 8. Heartbeat Monitoring

Each major ECU transmits an independent heartbeat message.

| CAN ID  | ECU                   | Period |
| ------- | --------------------- | ------ |
| `0x110` | Passenger Request ECU | 200 ms |
| `0x111` | Position/Sensor ECU   | 200 ms |
| `0x112` | Controller ECU        | 200 ms |
| `0x113` | Motor ECU             | 200 ms |
| `0x114` | Door ECU              | 200 ms |

The Diagnostic ECU records the arrival time of each heartbeat.

If a heartbeat is not received within the configured timeout period, the corresponding ECU is considered unavailable and a diagnostic fault is generated.

## 9. CAN Network Requirements Coverage

The CAN design provides:

* 14 unique CAN messages.
* More than 2 periodic messages.
* More than 2 event-triggered messages.
* Defined message ownership.
* Defined receivers.
* Defined transmission rates.
* Defined functional message groups.
* Dedicated diagnostic and safety communication.

The CAN network therefore satisfies the CAN Network Design requirements while providing the communication structure required by the six-ECU distributed elevator system.

