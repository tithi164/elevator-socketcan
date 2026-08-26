# Distributed Elevator Control System Using SocketCAN

A software-only distributed elevator control system implemented using Linux SocketCAN and Python.

The project models a multi-ECU elevator system where independent software ECUs communicate over a virtual CAN network (`vcan0`) to perform passenger request handling, elevator movement, motor and door control, diagnostics, fault detection, and recovery.

---

## 1. Project Overview

The system is divided into independent ECUs, each responsible for a specific function of the elevator.

The ECUs communicate using standard CAN frames through the Linux SocketCAN interface `vcan0`.

The project demonstrates:

- Distributed ECU architecture
- CAN communication
- Elevator control logic
- Sensor and actuator simulation
- ECU heartbeat monitoring
- Fault detection and recovery
- Console-based HMI
- End-to-end system operation

---

## 2. ECU Architecture

The system contains six ECUs and one separate HMI application.

| ECU | Responsibility |
| --- | --- |
| Passenger Request ECU | Accepts destination floor requests |
| Position/Sensor ECU | Simulates elevator position and current floor |
| Controller ECU | Performs elevator control and state management |
| Motor ECU | Controls simulated motor operation |
| Door ECU | Controls simulated door operation |
| Diagnostic ECU | Monitors ECU health and detects faults |

The HMI is a separate monitoring application and is not considered an ECU.

### Architecture

```text
              Passenger Request ECU
                       |
                  Floor Request
                       |
                       v
                Controller ECU
                  /          \
                 /            \
                v              v
           Motor ECU        Door ECU
                ^
                |
       Position/Sensor ECU

          Diagnostic ECU
                |
                v
             vcan0

        All ECUs communicate
          through SocketCAN
```

---

## 3. CAN Communication

The project uses the Linux SocketCAN virtual interface:

```text
vcan0
```

The main CAN messages are:

| CAN ID | Message | Type |
| --- | --- | --- |
| `0x100` | Floor Request | Event-triggered |
| `0x101` | Current Floor | Periodic |
| `0x102` | Position Status | Periodic |
| `0x103` | Motor Status | Periodic |
| `0x104` | Door Status | Periodic |
| `0x110` - `0x114` | ECU Heartbeats | Periodic |
| `0x200` | Motor Command | Event-triggered |
| `0x201` | Door Command | Event-triggered |
| `0x202` | Controller Status | Periodic |
| `0x300` | Safety Command | Event-triggered |

Detailed signal definitions and the complete CAN matrix are provided in the System Design Report.

---

## 4. Project Structure

```text
elevator_socketcan/
|
├── src/
│   ├── can_utils.py
│   ├── request_ecu.py
│   ├── position_sensor_ecu.py
│   ├── controller_ecu.py
│   ├── motor_ecu.py
│   ├── door_ecu.py
│   ├── diagnostic_ecu.py
│   └── hmi.py
|
├── tests/
|
├── .gitignore
└── README.md
```

The `can_utils.py` module provides common SocketCAN communication functions, CAN frame handling, signal encoding/decoding, and timestamp generation.

---

## 5. Requirements

- Linux
- Python 3
- Linux SocketCAN
- Virtual CAN (`vcan0`)

Create the virtual CAN interface:

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

Verify the interface:

```bash
ip link show vcan0
```

---

## 6. Running the System

From the project directory:

```bash
cd ~/elevator_socketcan
```

Run each ECU in a separate terminal.

### Terminal 1 - Passenger Request ECU

```bash
python3 -m src.request_ecu
```

### Terminal 2 - Position/Sensor ECU

```bash
python3 -m src.position_sensor_ecu
```

### Terminal 3 - Controller ECU

```bash
python3 -m src.controller_ecu
```

### Terminal 4 - Motor ECU

```bash
python3 -m src.motor_ecu
```

### Terminal 5 - Door ECU

```bash
python3 -m src.door_ecu
```

### Terminal 6 - Diagnostic ECU

```bash
python3 -m src.diagnostic_ecu
```

### Terminal 7 - HMI

```bash
python3 -m src.hmi
```

---

## 7. Normal Operation

A typical operation begins when the passenger enters a destination floor:

```text
Enter destination floor (1-5): 5
```

The Passenger Request ECU sends a floor request to the Controller ECU.

The Controller ECU determines the required direction and commands the Motor ECU.

The Position/Sensor ECU simulates movement between floors.

When the target floor is reached:

```text
Motor -> STOP
Door  -> OPEN
Door  -> CLOSE
System -> IDLE
```

The HMI provides a consolidated view of the current floor, requested floor, controller state, actuator status, ECU status, and diagnostic information.

---

## 8. Diagnostics and Fault Handling

The Diagnostic ECU monitors the health of the other ECUs using periodic heartbeat messages.

The system supports:

- Heartbeat timeout detection
- ECU/node failure detection
- Invalid position detection
- Diagnostic fault logging
- ECU recovery detection
- System recovery reporting

Example fault:

```text
FAULT: Controller ECU heartbeat timeout
```

Example recovery:

```text
RECOVERY: Controller ECU heartbeat restored
SYSTEM RECOVERY: All monitored ECUs operational
```

Diagnostic events are also recorded in the diagnostic log during execution.

---

## 9. Verification

The system was verified through:

- Normal elevator operation
- Floor request handling
- Motor movement and stopping
- Door operation
- Position monitoring
- ECU heartbeat monitoring
- ECU failure simulation
- Invalid position fault injection
- Fault recovery
- HMI status monitoring
- End-to-end distributed operation

Detailed test cases, screenshots, observations, and results are provided in the Test Report.

---

## 10. Demonstration

The project demonstrates:

1. Distributed ECU operation
2. CAN communication over SocketCAN
3. Elevator movement and control
4. Diagnostic monitoring
5. Fault injection
6. Fault recovery
7. End-to-end system behavior

CAN traffic can also be observed using:

```bash
candump vcan0
```

---

## 11. Technology Used

- Linux
- Python 3
- Linux SocketCAN
- Virtual CAN (`vcan0`)
- Standard CAN frames
- CAN RAW sockets
- Multi-process ECU applications

---

## 12. Documentation

The detailed project documentation is provided separately as part of the submission:

- System Design Report
- Test Report

The reports contain the detailed architecture, CAN matrix, signal definitions, design decisions, test cases, screenshots, results, observations, and conclusions.

---

## 13. Conclusion

This project demonstrates a software-only distributed elevator control system using Linux SocketCAN.

Independent ECUs communicate through a virtual CAN network to perform elevator control, actuator simulation, monitoring, diagnostics, fault detection, and recovery.

The implementation provides an end-to-end demonstration of a CAN-based distributed control system.
