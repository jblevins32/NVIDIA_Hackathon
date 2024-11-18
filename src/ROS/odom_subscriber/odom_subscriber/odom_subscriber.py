import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point

class OdomSubscriber(Node):

    def __init__(self):
        super().__init__('odom_subscriber')
        position = Point()
        qos = QoSProfile(
                reliability = ReliabilityPolicy.BEST_EFFORT,
                durability = DurabilityPolicy.VOLATILE,
                history = HistoryPolicy.KEEP_LAST,
                depth=1
        )
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.listener_callback,
            qos
        )
        self.subscription

    def listener_callback(self, msg: Odometry):
        #self.get_logger().info('Laserscan Received')
        #self.get_logger().info(f"Range data: {msg.ranges[:5]}")
        position = msg.pose.pose.position
        
def main(args=None):
    rclpy.init(args=args)

    odom_subscriber = OdomSubscriber()

    rclpy.spin(odom_subscriber)

    # Shutdown ROS 2
    odom_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
