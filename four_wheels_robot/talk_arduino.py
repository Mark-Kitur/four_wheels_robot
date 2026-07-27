import random
import rclpy
from rclpy.node import Node
from serial import Serial
from rclpy.executors import MultiThreadedExecutor
import tty
import termios
import sys
import select

class ArduinoSerial(Node):
    def __init__(self):
        super().__init__("arduino_rpi_serial")
        self.ser = Serial(port="/dev/ttyACM0", baudrate=9600, timeout=1)
        # Timer calls the method without arguments
        self.timer = self.create_timer(2, self.send_commands)

    def send_commands(self, left=None, right=None):
        # If called by timer, left/right are None; generate random
        if left is None or right is None:
            left = 0
            right = 0

        try:
            if self.ser.is_open:
                self.ser.write(bytes([left, right])) 
                self.get_logger().info(f"Sent: {left}, {right}")
                self.ser.flush()

                data = self.ser.readline().decode().strip()
                if data:
                    value = int(data)
                    self.get_logger().info(f"Received: {value}")
        except Exception as e:
            self.get_logger().error(f"Serial error: {e}")

class KeyBoard(Node):
    def __init__(self, arduino_node):
        super().__init__("keyboard")
        self.arduino = arduino_node  # Store reference to the other node instance
        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)
        tty.setraw(self.fd) 
        self.timer = self.create_timer(0.1, self.read_keyboard)

    def read_keyboard(self):
        ready, _, _ = select.select([sys.stdin], [], [], 0.05)
        
        if ready:
            ch = sys.stdin.read(1)
            if ch:
                print(f"Key pressed: {ch}")
                if ch == 'q':
                    rclpy.shutdown()
                elif ch == "i":
                    # Call method on the stored instance
                    self.arduino.send_commands(200, 200)
                elif ch == "j":
                    self.arduino.send_commands(180, 220)
                elif ch == "l":
                    self.arduino.send_commands(220, 180)

    def destroy_node(self):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    
    node = ArduinoSerial()

    keyboard = KeyBoard(node)

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.add_node(keyboard)

    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Exiting...")
    finally:
        executor.shutdown()
        node.destroy_node()
        keyboard.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()   