# Magnetic Levitator - Project Status & Notes

This repository contains code and data for a magnetic levitation demonstrator using an Arduino Uno, an SS49E Hall-effect sensor, and an IRFZ44N MOSFET-driven electromagnet.

---

## Current status (what has been done so far)

- Baseline sensor data recorded (no object in the middle) and saved under src\value_recod:
  - Files follow the naming convention: `hall_data_(voltage)_(YYYYMMDD)_(HHMMSS).csv` (example: `hall_data_6.6V_20260311_224748.csv`).
  - The value-recording Arduino sketch and a Python plotting/logging script are present in that folder (used to acquire the CSV data).
- Controller code prepared in the `Controller` folder:
  - `controller.ino` contains a full PWM->offset lookup table derived from the recorded baseline, with integer values and a small smoothing window (5-sample moving average).
  - The sketch safely drives the MOSFET gate LOW during setup and prints `Raw_Hall,Calculated_Offset,Clean_Signal` to Serial (115200 baud). It accepts a PWM value (0-255) sent via Serial to apply to the coil.

---

## File locations

- src\value_recod/  — baseline CSV recordings, the Arduino recorder sketch, and a Python logging/plotting script
- Controller/       — final controller sketch `controller.ino` (lookup-table based offset cancellation)
- 49E_values_plot.ino/ — (legacy) recording sketch used in earlier testing

---

## How the interference cancellation works (current implementation)

1. Baseline: the hall sensor was measured at every PWM step with no object present.
2. Values were stored in a lookup table (one entry per PWM [0..255]) inside `controller.ino`.
3. The controller reads the raw Hall ADC, looks up the expected offset for the current PWM, subtracts it to produce `Clean_Signal` and prints integers to Serial.
4. The lookup table values are smoothed with a 5-sample moving average in the sketch to reduce measurement noise.

This makes `Clean_Signal` ~ 0 when no object is present, across PWM values.

---

## How to use the current controller sketch

1. Open `Controller/controller.ino` in the Arduino IDE.
2. Verify wiring: Hall sensor -> A0, MOSFET gate -> pin 5 (or change pin in the sketch to match your wiring), common ground with power supply.
3. Upload to an Arduino Uno.
4. Open Serial Monitor at 115200 baud and send an integer 0–255 followed by Enter to set PWM; the sketch will print `Raw_Hall,Calculated_Offset,Clean_Signal` as integers.

Safety: the sketch holds the MOSFET gate LOW during setup; still start testing with low PWM values (0–50).

---

## Remaining work / To implement

- PID integration: replace (or wrap) the manual PWM control with a PID loop that adjusts PWM to hold a desired height.
- Voltage and current sensing: integrate ACS712 (current) and a voltage divider or voltage sensor to monitor supply voltage and enable safety limits (overcurrent, undervoltage).
- UI: build or extend a GUI to monitor Hall, PWM, current, voltage, and allow setting target height and PID parameters in real time.

Suggested priorities:
1. Add current and voltage sensing and safety trip limits (protect hardware). 
2. Implement PID loop with conservative gains and test in small steps using the Serial-set PWM feature.
3. Add a simple UI for plotting and live control (reuse existing Python UI code as a starting point).

---

## Notes & gotchas

- Ensure the Arduino ADC reference (AREF) and wiring are the same as during baseline recording; changing reference (e.g., using internal 1.1V) will invalidate the lookup table.
- The lookup table is specific to the coil, power supply voltage, and sensor placement — re-measure if hardware changes.
- The current controller uses the MOSFET gate pin 5; update the code if you wire the MOSFET to a different PWM-capable pin.

---

