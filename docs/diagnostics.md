# Diagnostics Requirements

## 1. Overview

A dedicated Diagnostic ECU is implemented to monitor the distributed Elevator Control System.

The Diagnostic ECU operates independently from the normal elevator control logic and provides network supervision, fault detection, fault reporting, safety handling, recovery detection, and event logging.

---

## 2. Diagnostic ECU Responsibilities

The Diagnostic ECU is responsible for:

- Monitoring ECU heartbeats
- Detecting missing messages
- Detecting abnormal sensor values
- Generating fault reports
- Requesting safe operation
- Detecting recovery
- Maintaining an event log

---

## 3. Heartbeat Monitoring

Each monitored ECU periodically transmits a heartbeat.

| ECU | Heartbeat CAN ID | Period |
|---|---:|---:|
| Passenger Request ECU | `0x110` | 200 ms |
| Position/Sensor ECU | `0x111` | 200 ms |
| Controller ECU | `0x112` | 200 ms |
| Motor ECU | `0x113` | 200 ms |
| Door ECU | `0x114` | 200 ms |

The Diagnostic ECU records the time at which each heartbeat was last received.

A heartbeat timeout indicates possible ECU failure or communication loss.

The configured heartbeat timeout is:

```text
1000 ms

A startup grace period is provided so that the ECUs can initialize before timeout monitoring becomes active.

4. Missing Message Detection

When an ECU heartbeat is not received within the configured timeout, the Diagnostic ECU:

Identifies the affected ECU.
Records a fault.
Sends a fault status message.
Requests a safety stop where required.
Logs the event.

Example:

FAULT: Position/Sensor ECU heartbeat timeout
5. Sensor Fault Detection

The Diagnostic ECU validates Position Status messages received on CAN ID 0x102.

Valid values are:

0
1
2
3

A value outside this range is treated as an invalid sensor value.

Example fault injection:

cansend vcan0 102#FF

The Diagnostic ECU detects:

FAULT: Invalid position status

and transmits:

SAFETY_STOP
6. Safety Response

The Diagnostic ECU uses CAN ID 0x300 for safety commands.

Value	Meaning
0	SAFETY_NORMAL
1	SAFETY_STOP
2	SAFETY_EMERGENCY

For detected faults, the Diagnostic ECU requests a safety stop.

The Controller then commands the Motor ECU to stop and enters the SAFE state.

7. Fault Reporting

Diagnostic fault information is transmitted using CAN ID 0x301.

Code	Fault
0x0000	No fault
0x0001	Heartbeat timeout
0x0002	Invalid position
0x0003	Door fault
0x0004	Motor fault
0x0005	ECU failure
0x0006	Recovery

The HMI uses the diagnostic information to display the current system fault.

8. Recovery

The Diagnostic ECU monitors the system after a fault.

For a heartbeat failure, recovery occurs when the affected ECU resumes heartbeat transmission.

For an invalid position fault, recovery occurs when valid Position Status messages resume.

When no active faults remain, the Diagnostic ECU sends:

SAFETY_NORMAL

The Controller can then leave SAFE and return to normal operation.

9. Event Logging

Diagnostic events are stored in:

logs/diagnostic.log

Events include:

Diagnostic ECU startup
Heartbeat timeout
Sensor fault
Recovery
System recovery
Diagnostic ECU shutdown

Example:

2026-08-23 17:05:44 | FAULT: Invalid position status
2026-08-23 17:05:45 | RECOVERY: Invalid position status restored
2026-08-23 17:05:45 | SYSTEM RECOVERY: All monitored systems operational
10. Diagnostic Verification

The Diagnostic ECU was verified using:

Missing heartbeat injection through ECU shutdown
Invalid position status injection
Fault reporting through the HMI
Safety-state verification
ECU recovery
Automatic system recovery

The diagnostic subsystem therefore provides both fault detection and recovery functionality required by the assignment.


