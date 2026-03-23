# Magnetic Levitator - Control Interface

A closed-loop magnetic levitation system with real-time monitoring and control interface.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install pyserial matplotlib
```

### 2. Upload Arduino Code
- Open Arduino IDE
- Load: `49E_values_plot.ino/49E_values_plot.ino.ino`
- Select **Arduino Uno** as your board
- Select your COM port
- Upload the sketch
- **CLOSE Arduino IDE completely** (important!)

### 3. Run the Interface
```bash
python magnetic_levitator_ui.py
```

**If you get "No module named 'serial'" error:**
```bash
# Windows - use the virtual environment
.venv\Scripts\python.exe magnetic_levitator_ui.py

# Or install globally
pip install pyserial matplotlib
```

### 4. Connect & Control
- Use Port ◄► buttons to select your Arduino's COM port
- Click **Connect** (status turns GREEN)
- Adjust PWM with slider or quick buttons (0%, 25%, 50%, 75%, 100%)
- **⚠️ START LOW! Begin at 0 and increase gradually**

---

## 📖 Project Overview
This project involves designing and building a closed-loop magnetic levitation system from scratch for theoretical proof and mechatronics application. Unlike simple kits, this build utilizes a custom-wound electromagnet made from a repurposed transformer C-core (30x15mm) to levitate ferromagnetic objects weighing 10–20g.

The system is designed for variable-point levitation, allowing the user to switch between specific heights—such as 10mm, 13mm, and 15mm—using a potentiometer. It features a "Real Deal" monitoring suite that tracks real-time current, voltage, and position to implement a software-based safety "watchdog".

## Technical Architecture

**Controller:** Arduino Uno running a PID (Proportional-Integral-Derivative) algorithm to stabilize the inherently unstable magnetic field.

**Actuator:** An 800-turn coil (0.80mm copper wire) driven by an IRFZ44N MOSFET at 12V DC.

**Feedback Loop:** An SS49E Linear Hall Effect sensor provides analog position data, while an ACS712 and an MH-Electronics Voltage Sensor monitor energy consumption.

**Safety:** A 1N5400 flyback diode protects the electronics from inductive spikes, complemented by a 5-minute thermal shutdown and overcurrent protection in the code.

## Pin Configuration (Arduino Uno)

```cpp
const int hallPin = A0;    // SS49E Hall Sensor (Position)
const int potPin = A1;     // Height Selector Potentiometer
const int currentPin = A2; // ACS712 Current Sensor
const int voltPin = A3;    // MH Voltage Sensor
const int coilPin = 3;     // MOSFET Gate Control (PWM) - Arduino Uno
```

---

## 🎮 Using the Interface

### Connection
1. Use **Port ◄►** buttons to select your Arduino's COM port
2. Click **"Refresh Ports"** if your port doesn't appear
3. Click **"Connect"** - status turns GREEN

### PWM Control (Magnetic Field Strength)
- **Drag slider:** 0-255 (0% to 100% magnetic field)
- **Quick buttons:** 0%, 25%, 50%, 75%, 100%
- **Real-time adjustment** while system is running
- **⚠️ PWM pin connected to Arduino Uno pin 3**

### Real-Time Displays
- **Hall Sensor Value:** Current magnetic field reading
- **Upper Graph:** Hall effect sensor readings (blue)
- **Lower Graph:** PWM output to electromagnet (red)
- **Both graphs** show last 200 samples

---

## 📊 Understanding the Values

### Hall Sensor (0-1023)
- **~512:** No magnetic field (neutral)
- **<512:** Object moving away from sensor
- **>512:** Object approaching sensor
- Use these values to tune your PID when implementing it

### PWM (0-255)
- **0:** Electromagnet OFF
- **128:** 50% power
- **255:** Maximum magnetic field strength

---

## ⚠️ Safety Notes

1. The electromagnet can get **HOT** with prolonged use at high PWM
2. Start with **LOW PWM values (20-50)** for testing
3. Monitor current draw if you added the ACS712 sensor
4. Keep ferromagnetic objects away until you're ready to test
5. Have a kill switch (disconnect) ready

---

## 🔧 Troubleshooting

### ❌ "Port not found" / "No serial ports found"
- Make sure Arduino is connected and drivers installed
- Close Arduino IDE completely
- Click "Refresh Ports" in the UI
- Use Port ◄► buttons to cycle through available ports

### ❌ "Permission Error" / "Access denied"
- Arduino IDE is still running - close it completely
- Close any other serial monitor programs
- Disconnect and reconnect Arduino USB cable

### ❌ No data appearing
- Check baud rate is 115200 in both Arduino code and UI
- Verify Arduino code is uploaded correctly
- Try disconnecting and reconnecting in the UI

### ❌ PWM not responding
- Check MOSFET gate connected to Arduino Uno pin 3
- Verify gate resistor is in place (1kΩ recommended)
- Ensure common ground between Arduino and power supply
- Test MOSFET circuit with LED before using electromagnet

---

## 🎯 Next Steps for PID Implementation

Once you're comfortable with manual control, you can:
1. Note the Hall sensor neutral point (~512)
2. Observe how quickly values change with PWM adjustments
3. Use this data to tune your PID constants (Kp, Ki, Kd)
4. Modify Arduino code to include PID algorithm

---

## 📦 Features

- **Real-time monitoring:** Live Hall sensor readings and PWM output visualization
- **Interactive control:** Adjust magnetic field strength (0-255 PWM) with slider or preset buttons
- **Safety features:** Start at zero power, manual control, emergency disconnect
- **Data logging:** 200-sample rolling graph for both sensor and control signals