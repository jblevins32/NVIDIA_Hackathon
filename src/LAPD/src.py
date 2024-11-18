import rclpy
from ROS.laser_subscriber.laser_subscriber import laser_subscriber


def main(args=None):
    rclpy.init(args=args)

    laser_sub_node = laser_subscriber.LaserScanSubscriber()
    rclpy.spin(laser_sub_node)

    