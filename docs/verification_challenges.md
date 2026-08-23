# Verification Challenges

## 1. Overview

The Elevator Control System was verified using the five verification challenges specified in the assignment.

The challenges cover normal operation, communication loss, sensor faults, ECU failure, and recovery.

---

# Challenge 1: Normal Operation

## Objective

Verify that all ECUs communicate successfully and that the elevator performs a complete floor request.

## Procedure

1. Start all six ECUs.
2. Start the HMI.
3. Verify that all monitored ECUs are online.
4. Verify that the initial system state is IDLE.
5. Enter a destination floor using the Passenger Request ECU.
6. Observe the controller, motor, position, and door behavior.
7. Verify that the elevator reaches the requested floor.
8. Verify that the door opens and closes.
9. Verify that the system returns to IDLE.

## Expected Result

The elevator should:

```text
Receive request
      ↓
Close door
      ↓
Move toward destination
      ↓
Reach requested floor
      ↓
Stop motor
      ↓
Open door
      ↓
Close door
      ↓
Return to IDLE

Result

PASS

The system successfully completed an end-to-end floor request and returned to the normal IDLE state.

Challenge 2: Missing Message Detection
Objective

Verify that the Diagnostic ECU detects loss of communication from an ECU.

Procedure
Start the complete system.
Verify normal operation.
Stop the Position/Sensor ECU using Ctrl+C.
Wait for the configured heartbeat timeout.
Observe the Diagnostic ECU.
Observe the HMI.
Verify that the missing ECU is detected.
Verify that an appropriate safety response is generated.
Expected Result

The Diagnostic ECU should report:

FAULT: Position/Sensor ECU heartbeat timeout

The affected ECU should be reported as offline and the controller should enter a safe state.

Result

PASS

The Diagnostic ECU detected the missing Position/Sensor ECU heartbeat and generated a diagnostic fault.

Challenge 3: Sensor Fault
Objective

Verify detection of an invalid sensor value and safe system behavior.

Fault Injection

The Position Status message uses CAN ID 0x102.

A valid Position Status value is within the range 0–3.

The following command was used:

cansend vcan0 102#FF

The value FF represents decimal 255 and is outside the valid range.

Expected Result

The Diagnostic ECU should detect:

FAULT: Invalid position status

and transmit a safety stop command.

The Controller should enter:

SAFE

and the Motor should be:

STOPPED
Result

PASS

The invalid sensor value was detected and the elevator entered a safe state with the motor stopped.

Challenge 4: Node Failure
Objective

Verify system behavior when an ECU unexpectedly stops operating.

Procedure
Start the complete system.
Verify normal operation.
Stop the Position/Sensor ECU unexpectedly.
Wait for the heartbeat timeout.
Observe the Diagnostic ECU.
Observe the Controller.
Observe the HMI.
Expected Result

The Diagnostic ECU should detect the missing heartbeat and report:

FAULT: Position/Sensor ECU heartbeat timeout

The Controller should enter SAFE and the motor should be stopped.

Other ECUs should remain operational.

Result

PASS

The failed ECU was detected through heartbeat monitoring and the remaining system generated the required safety response.

Challenge 5: Recovery
Objective

Verify that the system recovers after the failed ECU is restored.

Procedure
Stop the Position/Sensor ECU.
Allow the Diagnostic ECU to detect the failure.
Restart the Position/Sensor ECU.
Wait for heartbeat restoration.
Observe the Diagnostic ECU.
Observe the Controller.
Observe the HMI.
Expected Result

The Diagnostic ECU should report recovery:

RECOVERY: Position/Sensor ECU heartbeat restored

The system should return to normal operation:

System Fault : NONE
Controller State : IDLE
Position/Sensor : ONLINE
Result

PASS

The Position/Sensor ECU recovered successfully and the system returned to normal operation.

6. Verification Summary
Challenge	Expected Behavior	Result
Normal Operation	Complete floor request	PASS
Missing Message Detection	Detect heartbeat timeout	PASS
Sensor Fault	Detect invalid sensor value	PASS
Node Failure	Detect failed ECU	PASS
Recovery	Restore normal operation	PASS

All five required verification challenges were successfully demonstrated.
