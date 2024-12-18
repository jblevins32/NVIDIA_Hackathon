import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from sensor_msgs.msg import LaserScan


class LaserScanSubscriber(Node):
    scan_current = LaserScan()

    def __init__(self):
        super().__init__('laser_scan_subscriber')

        qos = QoSProfile(
                reliability = ReliabilityPolicy.BEST_EFFORT,
                durability = DurabilityPolicy.VOLATILE,
                history = HistoryPolicy.KEEP_LAST,
                depth=1
        )
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.listener_callback,
            qos
        )
        self.subscription

    def listener_callback(self, msg: LaserScan):
        #self.get_logger().info('Laserscan Received')
        #self.get_logger().info(f"Range data: {msg.ranges[:5]}")
        scan_current = msg
        
def main(args=None):
    rclpy.init(args=args)

    laser_scan_subscriber = LaserScanSubscriber()

    rclpy.spin(laser_scan_subscriber)

    # Shutdown ROS 2
    laser_scan_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
