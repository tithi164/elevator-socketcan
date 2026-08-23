# Human Machine Interface (HMI)

## 1. Overview

The Elevator Control System includes a console-based Human Machine Interface (HMI) for observing distributed system behavior.

The HMI provides a centralized view of:

- Current floor
- Requested floor
- Controller state
- Position status
- Motor status
- Door status
- ECU availability
- System fault
- Last diagnostic event

The HMI receives information from the CAN network and does not directly control the elevator.

---

## 2. HMI Responsibilities

The HMI is responsible for:

1. Displaying the current elevator state.
2. Displaying the requested destination.
3. Displaying position information.
4. Displaying motor state.
5. Displaying door state.
6. Displaying the availability of monitored ECUs.
7. Displaying diagnostic fault information.
8. Displaying the latest diagnostic event.

---

## 3. Displayed Information

The HMI displays the following system information:

| Information | Source |
|---|---|
| Current Floor | Position/Sensor ECU |
| Requested Floor | Passenger Request / Controller |
| Controller State | Controller ECU |
| Position Status | Position/Sensor ECU |
| Motor Status | Motor ECU |
| Door Status | Door ECU |
| Passenger Request ECU | Heartbeat |
| Position/Sensor ECU | Heartbeat |
| Controller ECU | Heartbeat |
| Motor ECU | Heartbeat |
| Door ECU | Heartbeat |
| System Fault | Diagnostic ECU |
| Last Event | Diagnostic ECU |

---

## 4. Example Normal State

A normal system state is displayed approximately as:

```text
========================================
       ELEVATOR SYSTEM HMI
========================================

Current Floor       : 5
Requested Floor     : 5

Controller State    : IDLE
Position Status     : VALID
Motor Status        : STOPPED
Door Status         : CLOSED

----------------------------------------
ECU STATUS
----------------------------------------

Passenger Request   : ONLINE
Position/Sensor     : ONLINE
Controller          : ONLINE
Motor               : ONLINE
Door                : ONLINE

----------------------------------------
DIAGNOSTICS
----------------------------------------

System Fault        : NONE
Last Event          : System normal

========================================

5. Fault Display

When a diagnostic fault is detected, the HMI displays the fault condition.

For example, during an invalid position fault:

Controller State    : SAFE
Motor Status        : STOPPED
System Fault        : INVALID POSITION
Last Event          : INVALID POSITION

This allows the operator to immediately determine:

What fault occurred
Whether the controller entered a safe state
Whether the motor stopped
Which part of the system requires attention
6. ECU Availability

The HMI displays the communication status of the monitored ECUs.

Example:

Passenger Request   : ONLINE
Position/Sensor     : OFFLINE
Controller           : ONLINE
Motor                : ONLINE
Door                 : ONLINE

An ECU is considered offline when its heartbeat is no longer detected by the diagnostic monitoring mechanism.

7. Recovery Display

When a failed ECU returns to operation, the HMI returns to the normal system state after the Diagnostic ECU detects recovery.

Example:

Position/Sensor     : ONLINE
System Fault        : NONE
Controller State    : IDLE
Motor Status        : STOPPED

The Diagnostic ECU also records the recovery event in its event log.

8. HMI and CAN Communication

The HMI observes CAN messages from the distributed system.

Important messages include:

0x101 — Current Floor
0x102 — Position Status
0x103 — Motor Status
0x104 — Door Status
0x202 — Controller Status
0x301 — Fault Status

Heartbeat information is also used to display ECU availability.

9. HMI Role in Verification

The HMI is used during system verification to observe:

Normal Operation
Floor request
Elevator movement
Motor operation
Door operation
Return to IDLE
Fault Operation
ECU offline condition
Invalid sensor condition
SAFE controller state
Motor stopped state
Diagnostic fault
Recovery
ECU returns online
Fault clears
Controller returns to normal
System resumes operation

The HMI therefore provides a simple operator-level view of the complete distributed system.
