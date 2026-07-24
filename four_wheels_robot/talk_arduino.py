import random

import rclpy
from rclpy.node import Node
from serial import Serial


class ArduinoSerial(Node):

    def __init__(self):
        super().__init__("arduino_rpi_serial")

        self.ser = Serial(
            port="/dev/ttyACM0",
            baudrate=9600,
            timeout=1
        )

        self.timer = self.create_timer(3, self.send_commands)

    def send_commands(self):

        left = random.randint(150, 255)
        right = random.randint(150, 255)

        try:
            if self.ser.is_open:
                self.get_logger().info("Port is open")

                msg = f"{left},{right}\n"
                self.ser.write(bytes([230,230]))

                self.get_logger().info(f"Sent: {left}, {right}")

        except Exception as e:
            self.get_logger().error(f"Serial error: {e}")


def main(args=None):

    rclpy.init(args=args)

    node = ArduinoSerial()

    try:
        rclpy.spin(node)
    finally:
        node.ser.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()