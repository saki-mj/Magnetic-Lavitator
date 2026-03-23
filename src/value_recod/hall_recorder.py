"""
Hall Sensor Recorder
--------------------
Connects to the Arduino running value_recod.ino, sends the runcheck trigger,
and captures the live-streamed readings. All CSV assembly (pivoting by PWM,
averaging) is done here on the PC – the Arduino stores nothing.

Arduino streams lines between ##DATA_START## / ##DATA_END## in the format:
    <label>,<pwm>,<hall>     e.g.   Up1,0,512

This script builds one CSV row per PWM value:
    Voltage, PWM, Up1, Down1, Up2, Down2, Up3, Down3, Average

Usage:
    python hall_recorder.py

Requirements:  pip install pyserial
"""

import serial
import serial.tools.list_ports
import csv
import os
import sys
import time
from collections import defaultdict
from datetime import datetime

SWEEP_LABELS = ["Up1", "Down1", "Up2", "Down2", "Up3", "Down3"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def list_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found. Is the Arduino connected?")
        sys.exit(1)
    print("\nAvailable serial ports:")
    for i, p in enumerate(ports):
        print(f"  [{i}]  {p.device}  –  {p.description}")
    return [p.device for p in ports]


def choose_port(port_list):
    if len(port_list) == 1:
        print(f"Auto-selecting only port: {port_list[0]}")
        return port_list[0]
    while True:
        try:
            idx = int(input("\nEnter port number: "))
            if 0 <= idx < len(port_list):
                return port_list[idx]
        except ValueError:
            pass
        print("Invalid selection, try again.")


def choose_voltage():
    while True:
        v = input("\nEnter supply voltage (e.g. 12.5): ").strip()
        try:
            float(v)
            return v
        except ValueError:
            print("Please enter a valid number.")


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ── Main recorder ─────────────────────────────────────────────────────────────

def run():
    print("=" * 60)
    print("  MAGNETIC LEVITATOR – Hall Sensor Recorder")
    print("=" * 60)

    port_list = list_ports()
    port      = choose_port(port_list)
    volt_str  = choose_voltage()

    # Output file
    script_dir   = os.path.dirname(os.path.abspath(__file__))
    default_file = os.path.join(script_dir, f"hall_data_{volt_str}V_{timestamp()}.csv")
    print(f"\nOutput file: {default_file}")
    custom   = input("Press Enter to accept, or type a different path: ").strip()
    out_file = custom if custom else default_file

    print(f"\nConnecting to {port} at 115200 baud …")
    try:
        ser = serial.Serial(port, 115200, timeout=2)
    except serial.SerialException as e:
        print(f"ERROR: Could not open port – {e}")
        sys.exit(1)

    time.sleep(2)          # wait for Arduino reset
    ser.reset_input_buffer()

    trigger = f'runcheck"{volt_str}"\n'
    print(f"Sending: {trigger.strip()}")
    ser.write(trigger.encode("utf-8"))

    # ── Capture loop ──────────────────────────────────────────────────────────
    # data[pwm][label] = hall_value
    data        = defaultdict(dict)
    in_data     = False
    current_sweep = ""

    print("\nWaiting for Arduino …  (this takes a few minutes)\n")

    try:
        while True:
            raw = ser.readline()
            if not raw:
                continue

            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue

            # ---- Markers ----
            if line == "##DATA_START##":
                in_data = True
                print("  Receiving data …")
                continue

            if line == "##DATA_END##":
                print("  All sweeps received.\n")
                break

            if not in_data:
                print(f"  {line}")
                continue

            # ---- Sweep progress header lines (start with #) ----
            if line.startswith("#"):
                current_sweep = line.lstrip("#").strip()
                print(f"  {current_sweep}")
                continue

            # ---- Data line: label,pwm,hall ----
            parts = line.split(",")
            if len(parts) == 3:
                label, pwm_str, hall_str = parts
                try:
                    pwm  = int(pwm_str)
                    hall = int(hall_str)
                    data[pwm][label] = hall
                except ValueError:
                    pass  # ignore malformed lines

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        ser.close()

    if not data:
        print("ERROR: No data was captured. Check wiring and try again.")
        sys.exit(1)

    # ── Build and write CSV ───────────────────────────────────────────────────
    os.makedirs(os.path.dirname(os.path.abspath(out_file)), exist_ok=True)

    header = ["Voltage", "PWM"] + SWEEP_LABELS + ["Average"]

    with open(out_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for pwm in sorted(data.keys()):
            row_vals = [data[pwm].get(lbl, "") for lbl in SWEEP_LABELS]
            numeric  = [v for v in row_vals if isinstance(v, int)]
            avg      = round(sum(numeric) / len(numeric), 2) if numeric else ""
            writer.writerow([volt_str, pwm] + row_vals + [avg])

    print(f"Saved {len(data)} rows → {out_file}")
    print("Done. Run again with a different voltage for another dataset.")


if __name__ == "__main__":
    run()
