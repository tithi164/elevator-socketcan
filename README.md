# Distributed Elevator Control System Using SocketCAN

A software-only distributed elevator control system implemented using Linux SocketCAN and Python.

The project models a multi-ECU elevator system in which independent software ECUs communicate over a virtual CAN network (`vcan0`) to perform floor request handling, position monitoring, motor control, door control, diagnostics, fault detection, and recovery.

## 1. Problem Description

Modern elevator systems are distributed control systems consisting of multiple controllers, sensors, actuators, and diagnostic functions.

This project demonstrates how such a system can be designed, implemented, tested, and validated using a CAN-based communication architecture before physical hardware is available.

The elevator system accepts passenger floor requests, determines the required movement, controls the motor and doors, monitors elevator position, and continuously supervises ECU health.

The system also includes dedicated diagnostic functionality for detecting communication failures, ECU failures, and abnormal sensor information.

### System Objectives

The system is designed to:

* Handle passenger floor requests
* Monitor the current elevator floor
* Control elevator motor movement
* Control elevator door operation
* Detect invalid position information
* Detect missing ECU communication
* Detect ECU/node failures
* Generate diagnostic fault information
* Recover when failed ECUs return to operation
* Provide a Human Machine Interface (HMI)
* Demonstrate distributed ECU communication using SocketCAN

## 2. Functional Analysis

### Inputs

The system receives:

* Passenger destination floor
* Current elevator position
* Motor status
* Door status
* ECU heartbeat messages
* Safety commands
* Position status information

### Sensors

The software model contains:

* Position sensor
* Motor status feedback
* Door status feedback
* ECU heartbeat supervision

### Actuators

The system contains simulated:

* Elevator motor actuator
* Elevator door actuator

### User Interaction

The Passenger Request ECU provides a console interface:

```text
Enter destination floor (1-5):
```

The HMI provides a system-level view of:

* Current floor
* Requested floor
* Controller state
* Position status
* Motor status
* Door status
* ECU availability
* Diagnostic status
* Last detected event

### Outputs

The system generates:

* Motor commands
* Door commands
* Current floor messages
* Position status messages
* Motor status messages
* Door status messages
* ECU heartbeat messages
* Controller status messages
* Diagnostic fault and recovery events

## 3. ECU Identification

The system uses six independent ECUs.

| ECU                   | Responsibility                                                                |
| --------------------- | ----------------------------------------------------------------------------- |
| Passenger Request ECU | Accepts destination floor requests from the user                              |
| Position/Sensor ECU   | Simulates elevator position and provides current floor information            |
| Controller ECU        | Performs the main elevator control logic and state management                 |
| Motor ECU             | Receives motor commands and reports motor status                              |
| Door ECU              | Receives door commands and reports door status                                |
| Diagnostic ECU        | Monitors ECU communication, detects faults, logs events, and reports recovery |

The HMI operates as a separate monitoring application and is not considered an ECU.

## 4. ECU Architecture

The distributed system is organized as follows:

```text
                       +------------------------+
                       | Passenger Request ECU  |
                       +-----------+------------+
                                   |
                              Floor Request
                                   |
                                   v
                       +------------------------+
                       |     Controller ECU     |
                       +-----------+------------+
                                   |
                    +--------------+--------------+
                    |                             |
                    v                             v
             +-------------+               +-------------+
             |  Motor ECU  |               |   Door ECU  |
             +-------------+               +-------------+
                    ^
                    |
             +------------------------+
             |   Position/Sensor ECU  |
             +------------------------+

                       +------------------------+
                       |     Diagnostic ECU     |
                       |   Network Supervision |
                       +------------------------+

                              SocketCAN
                                vcan0
```

All ECUs operate as independent applications and communicate through the SocketCAN interface.

## 5. CAN Network Design

The CAN network uses the Linux SocketCAN virtual interface:

```text
vcan0
```

The system uses standard 11-bit CAN identifiers.

### CAN Matrix

| CAN ID  | Transmitter           | Receiver             | Signal / Message  | Type            |
| ------- | --------------------- | -------------------- | ----------------- | --------------- |
| `0x100` | Passenger Request ECU | Controller ECU       | Floor Request     | Event-triggered |
| `0x101` | Position/Sensor ECU   | Controller ECU / HMI | Current Floor     | Periodic        |
| `0x102` | Position/Sensor ECU   | Diagnostic ECU / HMI | Position Status   | Periodic        |
| `0x103` | Motor ECU             | Controller ECU / HMI | Motor Status      | Periodic        |
| `0x104` | Door ECU              | Controller ECU / HMI | Door Status       | Periodic        |
| `0x110` | Passenger Request ECU | Diagnostic ECU       | Heartbeat         | Periodic        |
| `0x111` | Position/Sensor ECU   | Diagnostic ECU       | Heartbeat         | Periodic        |
| `0x112` | Controller ECU        | Diagnostic ECU       | Heartbeat         | Periodic        |
| `0x113` | Motor ECU             | Diagnostic ECU       | Heartbeat         | Periodic        |
| `0x114` | Door ECU              | Diagnostic ECU       | Heartbeat         | Periodic        |
| `0x200` | Controller ECU        | Motor ECU            | Motor Command     | Event-triggered |
| `0x201` | Controller ECU        | Door ECU             | Door Command      | Event-triggered |
| `0x202` | Controller ECU        | HMI / Diagnostic ECU | Controller Status | Periodic        |
| `0x300` | Safety / Test Source  | Controller ECU       | Safety Command    | Event-triggered |

The system contains both periodic and event-triggered messages.

## 6. Message Definition

The implementation primarily uses unsigned 8-bit signals.

### 6.1 Floor Request

```text
CAN ID      : 0x100
Signal      : Destination Floor
Encoding    : uint8
Range       : 1-5
Unit        : Floor number
Type        : Event-triggered
```

### 6.2 Current Floor

```text
CAN ID      : 0x101
Signal      : Current Floor
Encoding    : uint8
Range       : 1-5
Unit        : Floor number
Type        : Periodic
```

### 6.3 Position Status

```text
CAN ID      : 0x102
Signal      : Position Status
Encoding    : uint8
Type        : Periodic
```

| Value | Meaning               |
| ----- | --------------------- |
| `0`   | Unknown               |
| `1`   | Valid                 |
| `2`   | Invalid               |
| `3`   | Position Sensor Fault |

### 6.4 Motor Status

```text
CAN ID      : 0x103
Encoding    : uint8
Type        : Periodic
```

### 6.5 Motor Command

```text
CAN ID      : 0x200
Encoding    : uint8
Type        : Event-triggered
```

| Value | Meaning |
| ----- | ------- |
| `0`   | STOP    |
| `1`   | UP      |
| `2`   | DOWN    |

### 6.6 Door Status

```text
CAN ID      : 0x104
Encoding    : uint8
Type        : Periodic
```

| Value | Meaning |
| ----- | ------- |
| `0`   | CLOSED  |
| `1`   | OPEN    |
| `2`   | OPENING |
| `3`   | CLOSING |

### 6.7 Door Command

```text
CAN ID      : 0x201
Encoding    : uint8
Type        : Event-triggered
```

| Value | Meaning |
| ----- | ------- |
| `0`   | CLOSE   |
| `1`   | OPEN    |

### 6.8 Controller Status

```text
CAN ID      : 0x202
Encoding    : uint8
Type        : Periodic
```

The Controller ECU implements the following states:

```text
IDLE
REQUEST_RECEIVED
DOOR_CLOSING
MOVING_UP
MOVING_DOWN
ARRIVED
DOOR_OPENING
DOOR_OPEN
SAFE
```

### 6.9 Heartbeat Messages

Each monitored ECU periodically transmits a heartbeat message.

| CAN ID  | ECU                   |
| ------- | --------------------- |
| `0x110` | Passenger Request ECU |
| `0x111` | Position/Sensor ECU   |
| `0x112` | Controller ECU        |
| `0x113` | Motor ECU             |
| `0x114` | Door ECU              |

The Diagnostic ECU uses these messages to supervise ECU availability.

## 7. ECU Development

Each ECU is implemented as a separate Python application with an independent responsibility.

### Project Structure

```text
elevator_socketcan/
│
├── src/
│   ├── can_utils.py
│   ├── request_ecu.py
│   ├── position_sensor_ecu.py
│   ├── controller_ecu.py
│   ├── motor_ecu.py
│   ├── door_ecu.py
│   ├── diagnostic_ecu.py
│   └── hmi.py
│
├── tests/
│
├── .gitignore
└── README.md
```

### CAN Communication Utilities

The common CAN communication functions are implemented in:

```text
src/can_utils.py
```

The module provides:

* CAN socket creation
* CAN message transmission
* CAN message reception
* uint8 encoding and decoding
* uint16 encoding and decoding
* Timestamp generation for diagnostic logging

## 8. Elevator Control Operation

The normal elevator operation follows this sequence:

```text
Passenger enters destination floor
              |
              v
     Passenger Request ECU
              |
              | CAN 0x100
              v
        Controller ECU
              |
              v
      Check current floor
              |
              v
       Check door status
              |
              v
        Motor Command
              |
              v
          Motor ECU
              |
              v
     Position/Sensor ECU
              |
              v
        Floor updates
              |
              v
       Target floor reached
              |
              v
          Motor STOP
              |
              v
          Door OPEN
              |
              v
          Door CLOSE
              |
              v
             IDLE
```

The Position/Sensor ECU simulates elevator movement between floors.

## 9. Controller ECU State Machine

The Controller ECU uses a state-based control strategy.

```text
                         +----------------+
                         |      IDLE      |
                         +-------+--------+
                                 |
                            Floor Request
                                 |
                                 v
                    +-------------------------+
                    |   REQUEST_RECEIVED      |
                    +------------+------------+
                                 |
                    +------------+------------+
                    |                         |
              Door not closed          Already at target
                    |                         |
                    v                         v
          +------------------+         +-------------+
          |  DOOR_CLOSING    |         |   ARRIVED   |
          +--------+---------+         +------+------+
                   |                          |
              Door closed                     |
                   |                          |
                   v                          |
        +------------------------+            |
        | MOVING_UP / MOVING_DOWN|            |
        +-----------+------------+            |
                    |                         |
              Target reached                  |
                    |                         |
                    +------------+------------+
                                 |
                                 v
                          +-------------+
                          |   ARRIVED   |
                          +------+------+
                                 |
                                 v
                          +-------------+
                          | DOOR_OPENING|
                          +------+------+
                                 |
                            Door open
                                 |
                                 v
                          +-------------+
                          |  DOOR_OPEN  |
                          +------+------+
                                 |
                            Door close
                                 |
                                 v
                                IDLE
```

If a safety condition is detected, the controller enters:

```text
SAFE
```

and commands the motor to stop.

## 10. Human Machine Interface

A console-based HMI is provided to observe the system behavior.

The HMI displays:

```text
SYSTEM STATUS

Current Floor
Requested Floor
Controller State
Position Status

ACTUATORS

Motor Status
Door Status

ECU STATUS

Passenger Request
Position/Sensor
Controller
Motor
Door

DIAGNOSTICS

System Fault
Last Event
```

The HMI provides a consolidated view of the distributed elevator system.

## 11. Diagnostics

The Diagnostic ECU is a dedicated network monitoring ECU.

Its responsibilities are:

* Monitor network traffic
* Monitor ECU heartbeats
* Detect missing messages
* Detect ECU/node failures
* Detect abnormal position information
* Generate fault reports
* Generate recovery reports
* Maintain event logs

The Diagnostic ECU supervises:

```text
Passenger Request ECU
Position/Sensor ECU
Controller ECU
Motor ECU
Door ECU
```

### Heartbeat Monitoring

Each monitored ECU periodically transmits a heartbeat.

If the heartbeat is not received within the configured timeout period, the Diagnostic ECU reports a fault.

Example:

```text
FAULT: Controller ECU heartbeat timeout
```

When the ECU resumes communication:

```text
RECOVERY: Controller ECU heartbeat restored
```

When all monitored ECUs are operational again:

```text
SYSTEM RECOVERY: All monitored ECUs operational
```

## 12. Fault Handling

The system supports the required fault conditions.

### 12.1 Missing Message Detection

An ECU can be stopped to simulate communication loss.

The Diagnostic ECU detects the missing heartbeat and generates a warning.

Example:

```text
FAULT: Position/Sensor ECU heartbeat timeout
```

### 12.2 Sensor Fault

An invalid position status can be introduced.

Example:

```text
FAULT: Invalid position status
```

The fault is reflected in the diagnostic output and HMI.

### 12.3 Node Failure

Any monitored ECU can be stopped unexpectedly.

The Diagnostic ECU identifies the failed ECU using heartbeat supervision.

### 12.4 Recovery

When the failed ECU is restarted, heartbeat transmission resumes.

The Diagnostic ECU reports the recovery:

```text
RECOVERY: <ECU> heartbeat restored
```

The system then returns to normal network operation.

## 13. Verification Challenges

The implementation supports the required verification challenges.

### Challenge 1: Normal Operation

Verify that:

* All ECUs communicate successfully
* A passenger request is transmitted
* The Controller ECU receives the request
* The motor moves in the correct direction
* The position changes
* The target floor is reached
* The motor stops
* The door opens
* The door closes
* The system returns to IDLE

### Challenge 2: Missing Message Detection

Stop one ECU during operation.

Verify:

* Missing communication is detected
* A diagnostic warning is generated
* The affected ECU is identified

Expected output:

```text
FAULT: <ECU> heartbeat timeout
```

### Challenge 3: Sensor Fault

Introduce an invalid position status.

Verify:

* The abnormal value is detected
* A fault is reported
* The fault appears on the HMI

Expected output:

```text
FAULT: Invalid position status
```

### Challenge 4: Node Failure

Stop one ECU unexpectedly.

Verify:

* The Diagnostic ECU detects the failure
* Remaining ECUs continue running
* Diagnostic information is generated

### Challenge 5: Recovery

Restart the failed ECU.

Verify:

* Heartbeat communication resumes
* Recovery is detected
* The system returns to normal operation

Expected output:

```text
RECOVERY: <ECU> heartbeat restored
SYSTEM RECOVERY: All monitored ECUs operational
```

## 14. Testing

Testing is divided into functional tests, fault tests, and integration tests.

### 14.1 Functional Tests

| Test Case                  | Expected Result                     |
| -------------------------- | ----------------------------------- |
| Floor request transmission | Controller receives requested floor |
| Current floor transmission | Controller receives current floor   |
| Motor command              | Motor ECU changes state             |
| Door command               | Door ECU changes state              |
| Position simulation        | Elevator moves between floors       |
| HMI monitoring             | Current system state is displayed   |

### 14.2 Fault Tests

| Test Case                  | Expected Result            |
| -------------------------- | -------------------------- |
| Stop Passenger Request ECU | Heartbeat timeout detected |
| Stop Position/Sensor ECU   | Heartbeat timeout detected |
| Stop Controller ECU        | Heartbeat timeout detected |
| Stop Motor ECU             | Heartbeat timeout detected |
| Stop Door ECU              | Heartbeat timeout detected |
| Invalid position status    | Diagnostic fault generated |
| Restart failed ECU         | Recovery detected          |

### 14.3 Integration Tests

The complete system is tested by running all ECUs simultaneously over `vcan0`.

The end-to-end operation verifies:

```text
User Request
     |
     v
Controller ECU
     |
     v
Motor ECU
     |
     v
Position/Sensor ECU
     |
     v
Target Floor
     |
     v
Door ECU
     |
     v
System returns to IDLE
```

## 15. Running the Project

### Prerequisites

The project requires:

* Linux
* Python 3
* SocketCAN support

### Create the Virtual CAN Interface

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

Verify the interface:

```bash
ip link show vcan0
```

### Start the ECUs

From the project root:

```bash
cd ~/elevator_socketcan
```

Run each application in a separate terminal.

#### Terminal 1 - Passenger Request ECU

```bash
python3 -m src.request_ecu
```

#### Terminal 2 - Position/Sensor ECU

```bash
python3 -m src.position_sensor_ecu
```

#### Terminal 3 - Controller ECU

```bash
python3 -m src.controller_ecu
```

#### Terminal 4 - Motor ECU

```bash
python3 -m src.motor_ecu
```

#### Terminal 5 - Door ECU

```bash
python3 -m src.door_ecu
```

#### Terminal 6 - Diagnostic ECU

```bash
python3 -m src.diagnostic_ecu
```

#### Terminal 7 - HMI

```bash
python3 -m src.hmi
```

## 16. Monitoring CAN Traffic

SocketCAN traffic can be monitored using `candump`.

Run:

```bash
candump vcan0
```

To monitor a specific CAN ID:

```bash
candump vcan0,100:7FF
```

The CAN ID and payload can then be observed directly on the virtual CAN network.

## 17. Example Normal Operation

A passenger enters a destination floor:

```text
Enter destination floor (1-5): 5
```

The Passenger Request ECU transmits:

```text
Floor Request | ID: 0x100 | Floor: 5
```

The Controller ECU receives the request:

```text
Floor Request Received | Target: 5
Motor Command | ID: 0x200 | UP
```

The Position/Sensor ECU simulates elevator movement:

```text
Position | Floor: 2 | Direction: UP
Position | Floor: 3 | Direction: UP
Position | Floor: 4 | Direction: UP
Position | Floor: 5 | Direction: UP
```

After reaching the target floor, the Controller ECU stops the motor and operates the door.

The system then returns to the `IDLE` state.

## 18. Demonstration

The project demonstration covers:

1. Distributed system operation
2. CAN traffic between ECUs
3. Diagnostic functionality
4. Fault injection
5. Fault recovery
6. End-to-end system behavior

The demonstration can be observed through:

* Individual ECU terminals
* Diagnostic ECU output
* HMI
* SocketCAN traffic

## 19. Project Verification

The completed system demonstrates:

* Distributed software ECU architecture
* SocketCAN communication
* CAN network design
* CAN matrix implementation
* Signal definition and encoding
* Periodic communication
* Event-triggered communication
* State-based elevator control
* Sensor simulation
* Actuator simulation
* Human Machine Interface
* Network diagnostics
* Missing message detection
* Sensor fault detection
* ECU/node failure detection
* Fault recovery
* End-to-end system validation

## 20. Technology Used

* Linux
* Python 3
* SocketCAN
* Virtual CAN (`vcan0`)
* CAN RAW sockets
* Standard CAN frames
* Multi-terminal ECU execution

## 21. Conclusion

This project demonstrates a complete software-only distributed elevator control system using SocketCAN.

The elevator is divided into independent ECUs with clearly defined responsibilities. CAN messages provide communication between the ECUs, while the Diagnostic ECU supervises network health and detects abnormal conditions.

The combination of distributed control, sensor and actuator simulation, HMI monitoring, diagnostics, fault injection, and recovery provides an end-to-end demonstration of a CAN-based distributed control system.
