import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class LaserScanSubscriber(Node):
    def __init__(self):
        super().__init__('laser_scan_subscriber')
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.listener_callback,
            10
        )
        self.subscription

    def listener_callback(self, msg: LaserScan):
        self.get_logger().info('Laserscan Received')
        self.get_logger().info(f"Range data: {msg.ranges[:5]}")
        
def main(args=None):
    rclpy.init(args=args)

    laser_scan_subscriber = LaserScanSubscriber()

    rclpy.spin(laser_scan_subscriber)

    # Shutdown ROS 2
    laser_scan_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
