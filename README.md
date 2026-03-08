# Magnetic-Project Brief: Precision Magnetic Levitator (C-Core)
This project involves designing and building a closed-loop magnetic levitation system from scratch for theoretical proof and mechatronics application. Unlike simple kits, this build utilizes a custom-wound electromagnet made from a repurposed transformer C-core (30x15mm) to levitate ferromagnetic objects weighing 10–20g.

The system is designed for variable-point levitation, allowing the user to switch between specific heights—such as 10mm, 13mm, and 15mm—using a potentiometer. It features a "Real Deal" monitoring suite that tracks real-time current, voltage, and position to implement a software-based safety "watchdog".

Technical Architecture

Controller: Arduino Uno running a PID (Proportional-Integral-Derivative) algorithm to stabilize the inherently unstable magnetic field.

Actuator: An 800-turn coil (0.80mm copper wire) driven by an IRFZ44N MOSFET at 12V DC.

Feedback Loop: An SS49E Linear Hall Effect sensor provides analog position data, while an ACS712 and an MH-Electronics Voltage Sensor monitor energy consumption.

Safety: A 1N5400 flyback diode protects the electronics from inductive spikes, complemented by a 5-minute thermal shutdown and overcurrent protection in the code.Lavitator
