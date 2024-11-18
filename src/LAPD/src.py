import rclpy
from ROS.laser_subscriber.laser_subscriber import laser_subscriber
from sensor_msgs.msg import LaserScan

import torch


def LocateFromBB(yoloData,lidarScan):
    '''
    
    Args:
    yoloData: torch tensor of the following entries
       id | class | top left x |y |bottom right x| y|
    lidarScan: lidar scan from the current frame    
    
    Check for valid BBs and label with distance from current robot.

    #for BBs that meet check, take the average of the lidar readings between two x values.
    '''

    # check that the detected object's lower and upper y includes lidar height
    
    # check that the lower and upper x is within scan range of the lidar.



def angles2x(left,right):
    '''
    Translate angles on Lidar scan to xy on camera image.
    '''
    range = left - right

def local2global(distance,angle,position):
    '''
    Helper method.
    Get distance and angle from current robot along with robot current position from odometry as input. Then apply forward transform to locate in global map. 
    '''


def main(args=None):
    rclpy.init(args=args)

    laser_sub_node = laser_subscriber.LaserScanSubscriber()
    rclpy.spin(laser_sub_node)

    scan = LaserScan()
    scan = laser_sub_node.scan_current

    #get scan readings from angles from -25 to 25 and overlay on image.


    # check that the start and end is about the full range

    # get increment and label which distances are at which angle

    # match each reading to image frame..

    # find which bounding box 




    