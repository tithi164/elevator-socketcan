# Testing Requirements

## 1. Overview

Testing was performed to verify the functional behavior, fault handling, diagnostics, recovery, and end-to-end integration of the Elevator Control System.

Testing was divided into:

1. Functional Tests
2. Fault Tests
3. Integration Tests

---

# 2. Functional Tests

## FT-01: CAN Message Transmission

### Objective

Verify that ECUs transmit their assigned CAN messages.

### Procedure

Run:

```bash
candump vcan0

Start the distributed system and observe CAN traffic.

Expected Result

Periodic heartbeat and status messages should be visible.

Result

PASS

FT-02: Floor Request
Objective

Verify that the Passenger Request ECU accepts a valid floor request.

Procedure

Enter:

5

at the Passenger Request ECU.

Expected Result

The Passenger Request ECU transmits CAN ID 0x100.

Result

PASS

FT-03: Elevator Movement
Objective

Verify that the Controller commands the motor according to the requested destination.

Procedure

Request a floor different from the current floor.

Expected Result

The Controller commands:

MOTOR_UP

or:

MOTOR_DOWN

The Position/Sensor ECU updates the current floor.

Result

PASS

FT-04: Door Operation
Objective

Verify correct door opening and closing.

Procedure

Complete a floor request.

Expected Result

The Controller commands the door to open after arrival and close before returning to IDLE.

Result

PASS

FT-05: HMI Behavior
Objective

Verify that the HMI displays current distributed system information.

Expected Result

The HMI displays:

Current floor
Requested floor
Controller state
Position status
Motor status
Door status
ECU availability
Fault status
Last event
Result

PASS

3. Fault Tests
FT-06: Missing Message
Objective

Verify missing heartbeat detection.

Procedure

Stop the Position/Sensor ECU.

Expected Result

The Diagnostic ECU detects:

Position/Sensor ECU heartbeat timeout
Result

PASS

FT-07: Invalid Sensor Value
Objective

Verify invalid sensor value detection.

Procedure

Inject:

cansend vcan0 102#FF
Expected Result

The Diagnostic ECU detects an invalid position status.

The Controller enters SAFE and the motor stops.

Result

PASS

FT-08: ECU Shutdown
Objective

Verify behavior when an ECU fails unexpectedly.

Procedure

Stop the Position/Sensor ECU using:

Ctrl+C
Expected Result

The Diagnostic ECU detects the missing heartbeat and generates a fault.

Result

PASS

FT-09: ECU Recovery
Objective

Verify that communication resumes after an ECU is restarted.

Procedure

Restart the Position/Sensor ECU.

Expected Result

The Diagnostic ECU detects heartbeat recovery and the system returns to normal operation.

Result

PASS

4. Integration Tests
IT-01: End-to-End Elevator Operation
Objective

Verify interaction between all distributed ECUs.

Procedure
Start all six ECUs.
Start the HMI.
Enter a destination floor.
Observe Controller behavior.
Observe Motor operation.
Observe Position updates.
Observe Door operation.
Verify final HMI state.
Expected Result

The elevator completes the requested journey and returns to IDLE.

Result

PASS

IT-02: Diagnostic Integration
Objective

Verify interaction between the Diagnostic ECU, Controller ECU, Motor ECU and HMI during a fault.

Procedure
Start the complete system.
Inject an invalid position status.
Observe the Diagnostic ECU.
Observe the Controller.
Observe the Motor.
Observe the HMI.
Expected Result
Invalid sensor value
        ↓
Diagnostic fault
        ↓
Safety stop
        ↓
Controller SAFE
        ↓
Motor STOPPED
        ↓
Fault displayed on HMI
Result

PASS

IT-03: Fault Recovery Integration
Objective

Verify that the complete system recovers after a fault.

Procedure
Introduce a fault.
Verify SAFE state.
Restore the fault condition.
Observe Diagnostic ECU recovery.
Observe Controller recovery.
Verify HMI status.
Perform another floor request.
Expected Result

The system returns to normal operation and accepts a new floor request.

Result

PASS

5. Test Summary
Test ID	Test	Result
FT-01	CAN Message Transmission	PASS
FT-02	Floor Request	PASS
FT-03	Elevator Movement	PASS
FT-04	Door Operation	PASS
FT-05	HMI Behavior	PASS
FT-06	Missing Message	PASS
FT-07	Invalid Sensor Value	PASS
FT-08	ECU Shutdown	PASS
FT-09	ECU Recovery	PASS
IT-01	End-to-End Operation	PASS
IT-02	Diagnostic Integration	PASS
IT-03	Fault Recovery Integration	PASS
6. Testing Conclusion

The functional, fault, and integration tests demonstrate that the distributed Elevator Control System operates correctly under normal conditions and responds appropriately to communication failures and invalid sensor data.

The system was also verified to recover after restoration of the failed or faulty condition.
