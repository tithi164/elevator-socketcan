# ECU Development

## 1. Overview

The Elevator Control System is implemented as a distributed software system consisting of six independent Electronic Control Unit (ECU) applications.

Each ECU has a clearly defined responsibility and communicates with other ECUs through the Linux SocketCAN interface `vcan0`.

The six ECUs are:

1. Passenger Request ECU
2. Position/Sensor ECU
3. Controller ECU
4. Motor ECU
5. Door ECU
6. Diagnostic ECU

Each ECU is implemented as an independent Python application.

---

## 2. ECU Architecture

```text
                         +-------------------------+
                         | Passenger Request ECU   |
                         | Floor request handling  |
                         +------------+------------+
                                      |
                                    0x100
                                      |
                                      v
                         +-------------------------+
                         |      Controller ECU     |
                         | Elevator control logic  |
                         +------+-------------+----+
                                |             |
                              0x200         0x201
                                |             |
                                v             v
                     +---------------+   +---------------+
                     |   Motor ECU   |   |    Door ECU   |
                     | Motor control |   | Door control  |
                     +-------+-------+   +-------+-------+
                             ^
                             |
                         0x101 / 0x102
                             |
                     +---------------+
                     | Position /    |
                     | Sensor ECU    |
                     +---------------+

                     Heartbeat monitoring
                       0x110–0x114
                             |
                             v
                     +---------------+
                     | Diagnostic ECU|
                     | Fault monitor |
                     +-------+-------+
                             |
                       0x300 / 0x301
                             |
                             v
                     Controller / HMI
                     
                     
3. Passenger Request ECU
Responsibility

The Passenger Request ECU provides the user interaction for selecting a destination floor.

Inputs
User-entered destination floor
Outputs
Floor Request CAN message
ECU heartbeat
CAN Messages
CAN ID	Message	Type
0x100	Floor Request	Event-triggered
0x110	Heartbeat	Periodic
Operation

The user enters a floor from 1 to 5 through the console.

The ECU validates the input before transmitting the request.

Example:

Enter destination floor (1-5): 5

Floor Request | ID: 0x100 | Floor: 5

The Controller ECU receives the request and begins the elevator control sequence.

4. Position/Sensor ECU
Responsibility

The Position/Sensor ECU represents the elevator position sensing subsystem.

It maintains the simulated current floor and reports position information to the network.

Inputs
Motor status
Outputs
Current floor
Position status
ECU heartbeat
CAN Messages
CAN ID	Message	Type
0x101	Current Floor	Periodic
0x102	Position Status	Periodic
0x111	Heartbeat	Periodic
Operation

The elevator position is updated according to the motor direction.

The simulation represents movement between floors at a fixed interval.

Valid floors are:

1 – 5

The Position/Sensor ECU normally reports:

POSITION_VALID

The diagnostic system can detect invalid position values during fault injection.

5. Controller ECU
Responsibility

The Controller ECU is the central control node of the elevator system.

It receives floor requests and system status information and coordinates the Motor ECU and Door ECU.

Inputs
Floor request
Current floor
Motor status
Door status
Safety command
Outputs
Motor command
Door command
Controller status
ECU heartbeat
CAN Messages
CAN ID	Message	Type
0x200	Motor Command	Event-triggered
0x201	Door Command	Event-triggered
0x202	Controller Status	Periodic
0x112	Heartbeat	Periodic
Controller States

The Controller ECU implements a state-based control sequence.

IDLE
  |
  v
REQUEST_RECEIVED
  |
  v
DOOR_CLOSING
  |
  v
MOVING_UP / MOVING_DOWN
  |
  v
ARRIVED
  |
  v
DOOR_OPENING
  |
  v
DOOR_OPEN
  |
  v
IDLE

If a safety fault is received:

Any normal state
      |
      v
    SAFE
      |
      v
SAFETY_NORMAL
      |
      v
    IDLE
Normal Operation

For a request from Floor 1 to Floor 5:

Floor request received
        ↓
Check door state
        ↓
Close door if required
        ↓
Command motor UP
        ↓
Monitor current floor
        ↓
Reach Floor 5
        ↓
Stop motor
        ↓
Open door
        ↓
Close door
        ↓
Return to IDLE
6. Motor ECU
Responsibility

The Motor ECU controls and reports the simulated elevator motor state.

Inputs
Motor command from Controller ECU
Outputs
Motor status
ECU heartbeat
CAN Messages
CAN ID	Message	Type
0x103	Motor Status	Periodic
0x113	Heartbeat	Periodic
Motor States
MOTOR_STOP
MOTOR_UP
MOTOR_DOWN

The Motor ECU does not independently decide where the elevator should move.

The Controller ECU determines the required movement and sends the corresponding command.

7. Door ECU
Responsibility

The Door ECU controls the simulated elevator door and reports its state.

Inputs
Door command from Controller ECU
Outputs
Door status
ECU heartbeat
CAN Messages
CAN ID	Message	Type
0x104	Door Status	Periodic
0x114	Heartbeat	Periodic
Door States
DOOR_CLOSED
DOOR_OPEN
DOOR_OPENING
DOOR_CLOSING

Door movement is simulated using a configured movement time.

8. Diagnostic ECU
Responsibility

The Diagnostic ECU provides independent monitoring of the distributed system.

It does not control normal elevator movement.

Its responsibilities include:

Heartbeat monitoring
Invalid sensor detection
Fault reporting
Safety command generation
Recovery detection
Event logging
Inputs

Heartbeat and status messages from the other ECUs.

Outputs
Safety command
Fault status
Diagnostic event logs
CAN Messages
CAN ID	Message	Type
0x300	Safety Command	Event-triggered
0x301	Fault Status	Event-triggered
Heartbeat Monitoring

The Diagnostic ECU monitors:

0x110 Passenger Request ECU
0x111 Position/Sensor ECU
0x112 Controller ECU
0x113 Motor ECU
0x114 Door ECU

A missing heartbeat beyond the configured timeout is treated as an ECU communication fault.

The system uses a startup grace period to allow all ECUs to initialize before heartbeat timeout detection begins.

9. Fault Handling

The Diagnostic ECU can detect an invalid Position/Sensor status.

For example:

cansend vcan0 102#FF

The value FF represents decimal 255.

The valid Position Status range is:

0 – 3

Therefore, the Diagnostic ECU detects the value as invalid.

The resulting sequence is:

Invalid Position Status
        ↓
Diagnostic ECU
        ↓
FAULT_INVALID_POSITION
        ↓
SAFETY_STOP
        ↓
Controller SAFE
        ↓
Motor STOPPED

When valid position messages resume, the Diagnostic ECU clears the active sensor fault and sends:

SAFETY_NORMAL

The Controller can then return to normal operation.

10. ECU Independence

Each ECU is implemented as a separate application.

Example project structure:

src/
├── request_ecu.py
├── position_sensor_ecu.py
├── controller_ecu.py
├── motor_ecu.py
├── door_ecu.py
├── diagnostic_ecu.py
├── hmi.py
└── can_utils.py

The ECUs communicate through SocketCAN rather than direct Python function calls.

This provides a software representation of a distributed ECU architecture.

11. SocketCAN Communication

All ECUs use the Linux SocketCAN interface:

vcan0

CAN socket creation, message transmission, message reception, and signal encoding are handled through the common:

src/can_utils.py

This provides a consistent communication mechanism across the distributed applications.

12. Execution

Each ECU can be started independently from the project root.

Examples:

python3 -m src.request_ecu
python3 -m src.position_sensor_ecu
python3 -m src.controller_ecu
python3 -m src.motor_ecu
python3 -m src.door_ecu
python3 -m src.diagnostic_ecu
python3 -m src.hmi

The applications communicate through the shared vcan0 SocketCAN interface.

13. Verification

The ECU implementation is verified through:

Normal elevator operation
Floor request testing
CAN traffic observation
Missing heartbeat detection
Sensor fault injection
ECU shutdown testing
ECU recovery testing
End-to-end HMI observation

These tests verify both individual ECU behavior and distributed system interaction.


### 3. Save it.

Now our documentation flow is:

```text
docs/
├── functional_analysis.md       ✅ Task 1
├── ecu_identification.md        ✅ Task 2
├── can_matrix.md                ✅ Task 3
├── signal_specification.md      ✅ Task 4
└── ecu_development.md           ✅ Task 5
