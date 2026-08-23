# ECU Identification

## 1. ECU Architecture

The elevator system is divided into five independent software ECUs. Each ECU is implemented as a separate application and communicates with other ECUs through SocketCAN.

The five ECUs are:

1. Passenger Request ECU
2. Position/Sensor ECU
3. Controller ECU
4. Door & Motor ECU
5. Diagnostic & Safety ECU

## 2. Passenger Request ECU

### Responsibility

The Passenger Request ECU represents the passenger input interface for selecting a destination floor.

### Functions

* Accept destination floor input.
* Validate the requested floor.
* Generate floor request messages.
* Transmit floor requests through SocketCAN.
* Transmit ECU heartbeat information.

### Inputs

* Passenger destination floor.

### Outputs

* Floor Request CAN message.
* ECU Heartbeat CAN message.

---

## 3. Position/Sensor ECU

### Responsibility

The Position/Sensor ECU simulates elevator position and provides feedback about the current elevator floor.

### Functions

* Maintain simulated current-floor information.
* Provide position feedback.
* Transmit periodic position information.
* Provide heartbeat information.
* Support invalid position values during fault testing.

### Inputs

* Motor movement information.
* Fault-injection commands.

### Outputs

* Current Floor CAN message.
* Position/status information.
* ECU Heartbeat CAN message.

---

## 4. Controller ECU

### Responsibility

The Controller ECU is the main decision-making ECU of the elevator system.

### Functions

* Receive passenger floor requests.
* Validate destination requests.
* Determine elevator direction.
* Manage elevator operating states.
* Command elevator motor movement.
* Command door operation.
* Process position feedback.
* Determine when the destination floor has been reached.
* Command the elevator to stop.
* Process diagnostic safety commands.

### Inputs

* Floor Request.
* Current Floor.
* Door Status.
* Motor Status.
* Diagnostic/Fault Status.

### Outputs

* Motor Command.
* Door Command.
* Controller status information.
* ECU Heartbeat.

---

## 5. Motor ECU

### Responsibility

The Motor ECU represents the elevator motor control subsystem.

### Functions

* Receive motor commands from the Controller ECU.
* Simulate upward elevator movement.
* Simulate downward elevator movement.
* Stop elevator movement.
* Maintain motor operating state.
* Transmit motor status.
* Transmit ECU heartbeat information.
* Support node-failure testing.

### Inputs

* Motor Command.
* Safety/Emergency Stop command.

### Outputs

* Motor Status.
* Current movement direction.
* ECU Heartbeat.

---

## 6. Door ECU

### Responsibility

The Door ECU represents the elevator door control subsystem.

### Functions

* Receive door commands from the Controller ECU.
* Simulate door opening.
* Simulate door closing.
* Maintain door operating state.
* Transmit door status.
* Transmit ECU heartbeat information.
* Support door-related fault testing.

### Inputs

* Door Command.
* Safety-related commands where applicable.

### Outputs

* Door Status.
* ECU Heartbeat.

---

## 7. Diagnostic ECU

### Responsibility

The Diagnostic ECU monitors communication and system behavior and provides fault monitoring and diagnostic functionality.

### Functions

* Monitor ECU heartbeat messages.
* Monitor expected periodic CAN messages.
* Detect missing messages.
* Detect abnormal sensor values.
* Detect ECU/node failures.
* Generate diagnostic fault reports.
* Maintain timestamped event logs.
* Generate safety actions for critical faults.
* Detect ECU recovery.
* Report diagnostic status to the HMI.

### Inputs

* ECU Heartbeats.
* Position/Sensor messages.
* Motor status.
* Door status.
* Controller status.
* Fault/status messages.

### Outputs

* Diagnostic status.
* Fault reports.
* Safety commands.
* Recovery status.
* Event log entries.

---

## 8. ECU Communication Overview

```text
                  +------------------------+
                  | Passenger Request ECU  |
                  +-----------+------------+
                              |
                              | Floor Request
                              v
                    +----------------+
                    |    SocketCAN   |
                    |     vcan0      |
                    +-------+--------+
                            |
       +--------------------+---------------------+
       |                    |                     |
       v                    v                     v
+--------------+   +------------------+   +---------------+
| Controller   |   | Position/Sensor   |   | Diagnostic    |
| ECU          |   | ECU               |   | ECU           |
+------+-------+   +------------------+   +---------------+
       |
       | Commands
       |
       +------------------+
       |                  |
       v                  v
+--------------+   +--------------+
| Motor ECU    |   | Door ECU     |
+--------------+   +--------------+
       |                  |
       | Motor Status     | Door Status
       +------------------+
                 |
                 v
             SocketCAN
```

## 9. ECU Independence

Each ECU is implemented as a separate software application.

The six ECU applications are:

```text
request_ecu.py
position_sensor_ecu.py
controller_ecu.py
motor_ecu.py
door_ecu.py
diagnostic_ecu.py
```

The ECUs do not directly call functions inside other ECU applications. Communication occurs through CAN messages transmitted over the SocketCAN interface.

This allows each ECU to be started, stopped, monitored, tested, and recovered independently.

## 10. ECU Responsibilities Summary

| ECU                   | Primary Responsibility            |
| --------------------- | --------------------------------- |
| Passenger Request ECU | Floor request handling            |
| Position/Sensor ECU   | Position sensing and feedback     |
| Controller ECU        | Elevator control and coordination |
| Motor ECU             | Motor control                     |
| Door ECU              | Door control                      |
| Diagnostic ECU        | Fault monitoring and diagnostics  |

The six-ECU architecture exceeds the minimum ECU requirement and separates passenger interaction, sensing, control, motor actuation, door actuation, and diagnostics into independent software applications.

## 6. Diagnostic & Safety ECU

### Responsibility

The Diagnostic & Safety ECU monitors the distributed system and detects communication and operational faults.

### Functions

* Monitor ECU heartbeat messages.
* Monitor expected periodic CAN messages.
* Detect missing messages.
* Detect abnormal sensor values.
* Detect ECU/node failures.
* Generate diagnostic fault reports.
* Maintain timestamped event logs.
* Generate safety actions for critical faults.
* Detect ECU recovery.
* Report system diagnostic status.

### Inputs

* ECU Heartbeats.
* Sensor messages.
* Motor status.
* Door status.
* Controller status.
* Fault/status messages.

### Outputs

* Diagnostic status.
* Fault reports.
* Safety commands.
* Recovery status.
* Event log entries.

---

## 7. ECU Communication Overview

```text
                  +-----------------------+
                  | Passenger Request ECU |
                  +-----------+-----------+
                              |
                              | Floor Request
                              v
                    +----------------+
                    |    SocketCAN   |
                    |     vcan0      |
                    +-------+--------+
                            |
          +-----------------+------------------+
          |                 |                  |
          v                 v                  v
 +----------------+ +---------------+ +------------------+
 | Controller ECU | | Position/     | | Door & Motor ECU |
 |                | | Sensor ECU    | |                  |
 +-------+--------+ +---------------+ +--------+---------+
         |                                      |
         | Commands                             | Feedback
         +------------------+-------------------+
                            |
                            v
                 +------------------------+
                 | Diagnostic & Safety ECU|
                 +-----------+------------+
                             |
                             v
                            HMI
```

## 8. ECU Independence

Each ECU is implemented as an independent software application.

The ECUs do not directly call functions inside another ECU. Communication between ECUs occurs through CAN messages transmitted over the SocketCAN interface.

This provides a distributed architecture in which individual ECU applications can be started, stopped, tested, and recovered independently.

## 9. ECU Responsibilities Summary

| ECU                     | Primary Responsibility            |
| ----------------------- | --------------------------------- |
| Passenger Request ECU   | Floor request handling            |
| Position/Sensor ECU     | Position sensing and feedback     |
| Controller ECU          | Elevator control and coordination |
| Door & Motor ECU        | Door and motor control            |
| Diagnostic & Safety ECU | Fault monitoring and safety       |

The architecture satisfies the minimum requirement of four independent ECUs while providing separate functional responsibilities for passenger interaction, sensing, control, actuation, and diagnostics.
