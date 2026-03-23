"""
Magnetic Levitator Control Interface (Matplotlib Version)
Real-time Hall sensor monitoring and PWM control
No tkinter required!
"""

import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox
from matplotlib.animation import FuncAnimation
from collections import deque
import threading
import time


class MagneticLevitatorUI:
    def __init__(self):
        # Serial connection
        self.serial_port = None
        self.is_connected = False
        self.running = True
        
        # Data buffers
        self.max_data_points = 200
        self.hall_data = deque([0] * self.max_data_points, maxlen=self.max_data_points)
        self.pwm_data = deque([0] * self.max_data_points, maxlen=self.max_data_points)
        
        self.current_hall = 0
        self.current_pwm = 0
        self.pwm_value = 0
        
        # Get available ports
        self.ports = [port.device for port in serial.tools.list_ports.comports()]
        self.current_port_index = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create figure and subplots
        self.fig = plt.figure(figsize=(12, 8))
        self.fig.canvas.manager.set_window_title('Magnetic Levitator Control Interface')
        
        # Hall sensor plot
        self.ax_hall = plt.subplot2grid((4, 3), (0, 0), colspan=3)
        self.line_hall, = self.ax_hall.plot([], [], 'b-', linewidth=2, label='Hall Sensor')
        self.ax_hall.set_ylabel('Hall Sensor Value', fontsize=10, fontweight='bold')
        self.ax_hall.set_title('Real-Time Magnetic Field Sensor Data', fontsize=12, fontweight='bold')
        self.ax_hall.grid(True, alpha=0.3)
        self.ax_hall.legend(loc='upper right')
        self.ax_hall.set_ylim(0, 1023)
        self.ax_hall.set_xlim(0, self.max_data_points)
        
        # PWM plot
        self.ax_pwm = plt.subplot2grid((4, 3), (1, 0), colspan=3)
        self.line_pwm, = self.ax_pwm.plot([], [], 'r-', linewidth=2, label='PWM Output')
        self.ax_pwm.set_xlabel('Sample Number', fontsize=10)
        self.ax_pwm.set_ylabel('PWM Value', fontsize=10, fontweight='bold')
        self.ax_pwm.set_title('Magnetic Coil Drive Signal', fontsize=12, fontweight='bold')
        self.ax_pwm.grid(True, alpha=0.3)
        self.ax_pwm.legend(loc='upper right')
        self.ax_pwm.set_ylim(0, 255)
        self.ax_pwm.set_xlim(0, self.max_data_points)
        
        # PWM Slider
        ax_slider = plt.subplot2grid((4, 3), (2, 0), colspan=3)
        ax_slider.set_title('PWM Control (Magnetic Field Strength)', fontweight='bold')
        self.pwm_slider = Slider(ax_slider, 'PWM', 0, 255, valinit=0, valstep=1, color='orange')
        self.pwm_slider.on_changed(self.on_pwm_change)
        
        # Control buttons row 1
        btn_height = 0.05
        btn_width = 0.12
        
        # Quick PWM buttons
        ax_btn_0 = plt.axes([0.1, 0.30, btn_width, btn_height])
        self.btn_0 = Button(ax_btn_0, '0%', color='lightgray', hovercolor='gray')
        self.btn_0.on_clicked(lambda x: self.set_pwm(0))
        
        ax_btn_25 = plt.axes([0.24, 0.30, btn_width, btn_height])
        self.btn_25 = Button(ax_btn_25, '25%', color='lightblue', hovercolor='skyblue')
        self.btn_25.on_clicked(lambda x: self.set_pwm(64))
        
        ax_btn_50 = plt.axes([0.38, 0.30, btn_width, btn_height])
        self.btn_50 = Button(ax_btn_50, '50%', color='lightgreen', hovercolor='lightcoral')
        self.btn_50.on_clicked(lambda x: self.set_pwm(128))
        
        ax_btn_75 = plt.axes([0.52, 0.30, btn_width, btn_height])
        self.btn_75 = Button(ax_btn_75, '75%', color='lightyellow', hovercolor='yellow')
        self.btn_75.on_c
        licked(lambda x: self.set_pwm(191))
        
        ax_btn_100 = plt.axes([0.66, 0.30, btn_width, btn_height])
        self.btn_100 = Button(ax_btn_100, '100%', color='lightcoral', hovercolor='red')
        self.btn_100.on_clicked(lambda x: self.set_pwm(255))
        
        # Connection controls
        ax_connect = plt.axes([0.1, 0.22, 0.15, btn_height])
        self.btn_connect = Button(ax_connect, 'Connect', color='lightgreen', hovercolor='green')
        self.btn_connect.on_clicked(self.toggle_connection)
        
        ax_port_prev = plt.axes([0.27, 0.22, 0.08, btn_height])
        self.btn_port_prev = Button(ax_port_prev, '◄ Port', color='lightgray', hovercolor='gray')
        self.btn_port_prev.on_clicked(self.prev_port)
        
        ax_port_next = plt.axes([0.36, 0.22, 0.08, btn_height])
        self.btn_port_next = Button(ax_port_next, 'Port ►', color='lightgray', hovercolor='gray')
        self.btn_port_next.on_clicked(self.next_port)
        
        ax_refresh = plt.axes([0.46, 0.22, 0.12, btn_height])
        self.btn_refresh = Button(ax_refresh, 'Refresh Ports', color='lightyellow', hovercolor='yellow')
        self.btn_refresh.on_clicked(self.refresh_ports)
        
        # Status text
        self.status_text = self.fig.text(0.1, 0.17, self.get_status_text(), 
                                         fontsize=11, family='monospace',
                                         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.38, hspace=0.4)
        
        # Start animation
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=50, blit=False)
        
    def get_status_text(self):
        port_name = self.ports[self.current_port_index] if self.ports else "No ports found"
        status = "🟢 CONNECTED" if self.is_connected else "🔴 DISCONNECTED"
        
        return (f"Status: {status}\n"
                f"Serial Port: {port_name}\n"
                f"Hall Sensor: {self.current_hall:4d} | PWM: {self.current_pwm:3d} ({self.current_pwm*100/255:.0f}%)")
    
    def prev_port(self, event):
        if self.ports and not self.is_connected:
            self.current_port_index = (self.current_port_index - 1) % len(self.ports)
            self.status_text.set_text(self.get_status_text())
            self.fig.canvas.draw_idle()
    
    def next_port(self, event):
        if self.ports and not self.is_connected:
            self.current_port_index = (self.current_port_index + 1) % len(self.ports)
            self.status_text.set_text(self.get_status_text())
            self.fig.canvas.draw_idle()
    
    def refresh_ports(self, event):
        if not self.is_connected:
            self.ports = [port.device for port in serial.tools.list_ports.comports()]
            self.current_port_index = 0
            self.status_text.set_text(self.get_status_text())
            self.fig.canvas.draw_idle()
            print(f"Found {len(self.ports)} port(s)")
    
    def toggle_connection(self, event):
        if not self.is_connected:
            self.connect()
        else:
            self.disconnect()
    
    def connect(self):
        if not self.ports:
            print("No serial ports found!")
            return
            
        try:
            port = self.ports[self.current_port_index]
            print(f"Connecting to {port}...")
            self.serial_port = serial.Serial(port, 115200, timeout=0.1)
            time.sleep(2)  # Wait for Arduino to reset
            self.is_connected = True
            self.btn_connect.label.set_text('Disconnect')
            self.btn_connect.color = 'lightcoral'
            self.btn_connect.hovercolor = 'red'
            
            # Start reading thread
            self.read_thread = threading.Thread(target=self.read_serial, daemon=True)
            self.read_thread.start()
            
            print(f"Connected to {port}")
            
        except Exception as e:
            print(f"Connection error: {e}")
            self.is_connected = False
    
    def disconnect(self):
        self.is_connected = False
        if self.serial_port:
            self.serial_port.close()
        self.btn_connect.label.set_text('Connect')
        self.btn_connect.color = 'lightgreen'
        self.btn_connect.hovercolor = 'green'
        print("Disconnected")
    
    def read_serial(self):
        while self.is_connected:
            try:
                if self.serial_port and self.serial_port.in_waiting:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    if ',' in line:
                        parts = line.split(',')
                        if len(parts) == 2:
                            hall_value = int(parts[0])
                            pwm_value = int(parts[1])
                            
                            self.current_hall = hall_value
                            self.current_pwm = pwm_value
                            
                            self.hall_data.append(hall_value)
                            self.pwm_data.append(pwm_value)
                            
            except Exception as e:
                print(f"Read error: {e}")
    
    def on_pwm_change(self, value):
        pwm = int(value)
        self.pwm_value = pwm
        self.send_pwm(pwm)
    
    def set_pwm(self, value):
        self.pwm_slider.set_val(value)
        self.send_pwm(value)
    
    def send_pwm(self, value):
        if self.is_connected and self.serial_port:
            try:
                command = f"PWM:{value}\n"
                self.serial_port.write(command.encode())
            except Exception as e:
                print(f"Send error: {e}")
    
    def update_plot(self, frame):
        # Update status text
        self.status_text.set_text(self.get_status_text())
        
        # Update plots
        x_data = list(range(len(self.hall_data)))
        
        self.line_hall.set_data(x_data, list(self.hall_data))
        self.line_pwm.set_data(x_data, list(self.pwm_data))
        
        return self.line_hall, self.line_pwm, self.status_text
    
    def run(self):
        plt.show()
        self.running = False
        self.disconnect()


def main():
    print("=" * 60)
    print("  MAGNETIC LEVITATOR CONTROL INTERFACE")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Use 'Port ◄►' buttons to select your Arduino port")
    print("2. Click 'Connect' to establish connection")
    print("3. Use the PWM slider or quick buttons to control")
    print("4. Start with LOW values (0-50) for safety!")
    print("\n" + "=" * 60 + "\n")
    
    app = MagneticLevitatorUI()
    app.run()


if __name__ == "__main__":
    main()
