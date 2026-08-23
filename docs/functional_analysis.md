# Functional Analysis

## 1. System

**Distributed Fault-Tolerant Elevator Control and Safety System Using SocketCAN**

The system is a software-only distributed elevator control system implemented using Linux SocketCAN and a virtual CAN interface (`vcan0`).

The system models a five-floor elevator and demonstrates floor request handling, door control, motor control, and fault monitoring using multiple independent software ECUs.

## 2. System Objectives

The system shall:

* Accept passenger floor requests.
* Determine the required direction of elevator travel.
* Control simulated elevator movement between floors.
* Control elevator door opening and closing.
* Monitor elevator position.
* Exchange information between independent ECUs through SocketCAN.
* Detect missing CAN messages.
* Detect invalid sensor values.
* Detect ECU/node failures.
* Generate diagnostic information and event logs.
* Transition the elevator to a safe state when a critical fault occurs.
* Detect recovery of a failed ECU.
* Restore normal operation after successful recovery.
* Provide system status and diagnostic information through the Human Machine Interface (HMI).

## 3. Inputs

### 3.1 User Inputs

The primary user input is the requested destination floor.

Example:

```text
Destination Floor = 5
```

### 3.2 Sensor Inputs

The system receives simulated sensor information including:

* Current elevator floor
* Door position/status
* Motor status

### 3.3 CAN Communication Inputs

ECUs receive CAN messages containing:

* Floor requests
* Position feedback
* Door status
* Motor status
* ECU heartbeat information
* Diagnostic and fault information

### 3.4 Fault Injection Inputs

The verification system can introduce:

* Invalid sensor values
* Missing CAN messages
* ECU shutdown/failure

These inputs are used during fault and recovery testing.

## 4. Outputs

### 4.1 Actuator Outputs

The system generates:

* Motor UP command
* Motor DOWN command
* Motor STOP command
* Door OPEN command
* Door CLOSE command

### 4.2 CAN Communication Outputs

The ECUs transmit:

* Floor requests
* Sensor/status information
* Actuator commands
* ECU heartbeat messages
* Fault information
* Recovery information

### 4.3 Diagnostic Outputs

The Diagnostic ECU generates:

* Warnings
* Fault reports
* Safety actions
* Recovery notifications
* Timestamped event logs

### 4.4 HMI Outputs

The HMI displays:

* Current system status
* Current floor
* Requested floor
* Elevator direction
* Door state
* Motor state
* ECU communication status
* Active faults
* Diagnostic events

## 5. Sensors

The following sensors are simulated in software.

### 5.1 Position Sensor

Provides the current elevator floor.

Valid range:

```text
Floor 1 to Floor 5
```

### 5.2 Door Position Sensor

Provides the current door state:

```text
OPEN
CLOSED
OPENING
CLOSING
```

### 5.3 Motor Status Sensor

Provides the current motor state:

```text
STOPPED
MOVING_UP
MOVING_DOWN
```

## 6. Actuators

### 6.1 Elevator Motor

The simulated motor accepts:

```text
UP
DOWN
STOP
```

### 6.2 Elevator Door

The simulated door accepts:

```text
OPEN
CLOSE
```

The Door & Motor ECU executes these commands and provides status feedback through CAN messages.

## 7. User Interactions

During normal operation, the user interacts with the system by selecting a destination floor.

The HMI provides system observation including:

* Current floor
* Destination floor
* Elevator state
* Direction
* Door state
* Motor state
* ECU status
* Fault information
* Diagnostic events

Fault injection controls may also be provided for verification demonstrations. These are intended for testing rather than normal passenger operation.

## 8. Functional Block Diagram

```text
                    +---------------------+
                    |        USER         |
                    |                     |
                    |  Destination Floor  |
                    +----------+----------+
                               |
                               v
                    +---------------------+
                    | Passenger Request   |
                    |        ECU          |
                    +----------+----------+
                               |
                               | Floor Request
                               v
                     +------------------+
                     |    SocketCAN     |
                     |      vcan0       |
                     +--------+---------+
                              |
              +---------------+----------------+
              |               |                |
              v               v                v
     +----------------+ +-------------+ +-----------------+
     |   Controller   | | Position /  | | Door & Motor    |
     |      ECU       | | Sensor ECU  | |      ECU        |
     +-------+--------+ +------+------+ +--------+--------+
             |                 |                 |
             | Commands        | Feedback        | Status
             +-----------------+-----------------+
                               |
                               v
                     +---------------------+
                     | Diagnostic & Safety |
                     |        ECU          |
                     +----------+----------+
                                |
                                | Status / Faults
                                v
                     +---------------------+
                     |        HMI          |
                     |                     |
                     | System Status       |
                     | Sensor Values       |
                     | Actuator States     |
                     | Fault Information   |
                     +---------------------+

```

## 9. Normal Functional Flow

A normal elevator operation follows this sequence:

1. The user selects a destination floor.
2. The Passenger Request ECU validates the request.
3. The Passenger Request ECU transmits the floor request through SocketCAN.
4. The Controller ECU receives the request.
5. The Controller ECU determines the required direction.
6. The Controller commands the Door & Motor ECU to close the door.
7. The Door & Motor ECU reports the door status.
8. The Controller commands the motor to move.
9. The Position/Sensor ECU provides current-floor feedback.
10. The Controller compares the current floor with the requested destination.
11. The motor is stopped when the destination is reached.
12. The Controller commands the door to open.
13. The Door & Motor ECU reports the door-open status.
14. The elevator returns to the IDLE state.

## 10. Fault Functional Flow

Fault handling operates in parallel with normal elevator control.

```text
ECU / Sensor Activity
        |
        v
CAN Communication
        |
        v
Diagnostic & Safety ECU
        |
        +---- Missing message
        |
        +---- Invalid value
        |
        +---- ECU failure
        |
        v
Fault Detection
        |
        v
Fault Report
        |
        v
Safety Action
        |
        v
SAFE State
        |
        v
Recovery Detection
        |
        v
Return to Normal Operation
```

## 11. Functional Scope

The functional scope directly covers the required Elevator Control System functions:

* Floor request handling
* Door control
* Motor control
* Fault monitoring

The system additionally provides diagnostics, fault handling, recovery, and HMI-based system observation to satisfy the distributed-system, verification, and validation requirements.

