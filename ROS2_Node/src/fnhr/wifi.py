import socket
import struct
import Orders

import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class Controller(Node):
    # Initialize a TCP client socket using SOCK_STREAM
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip, server_port = "192.168.4.1", 65535

    def __init__(self):
        super().__init__('wifi_controller')
        self.tcp_client.settimeout(5)
        self.tcp_client.connect((self.host_ip, self.server_port))
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)

    def send(self, order):
        data = struct.pack("BBB", Orders.transStart,order,Orders.transEnd)

        # Establish connection to TCP server and exchange data
        self.tcp_client.sendall(data)

        # Read data from the TCP server and close the connection
        received = self.tcp_client.recv(1024)

def main(args=None):
    rclpy.init(args=args)

    controller = Controller()
    controller.send(Orders.requestCrawlForward)

    rclpy.spin(controller)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    controller.tcp_client.close()
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

