# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy, QoSHistoryPolicy
import numpy as np
import math

from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point
from std_msgs.msg import String
from std_msgs.msg import Float32MultiArray, MultiArrayDimension
from std_msgs.msg import Bool

class ObjectsInfoPublisher(Node):

    def __init__(self):
        super().__init__('colored_object_finder')

        # Initialize QoS profiles for different message types
        yolo_qos_profile = QoSProfile(
		    reliability=QoSReliabilityPolicy.BEST_EFFORT,
		    history=QoSHistoryPolicy.KEEP_LAST,
		    durability=QoSDurabilityPolicy.VOLATILE,
		    depth=1
		)

        lidar_qos_profile = QoSProfile(
		    reliability=QoSReliabilityPolicy.BEST_EFFORT,
		    history=QoSHistoryPolicy.KEEP_LAST,
		    durability=QoSDurabilityPolicy.VOLATILE,
		    depth=1
		)

        completion_qos_profile = QoSProfile(
		    reliability=QoSReliabilityPolicy.BEST_EFFORT,
		    history=QoSHistoryPolicy.KEEP_LAST,
		    durability=QoSDurabilityPolicy.VOLATILE,
		    depth=1
		)

        odom_qos_profile = QoSProfile(
		    reliability=QoSReliabilityPolicy.BEST_EFFORT,
		    history=QoSHistoryPolicy.KEEP_LAST,
		    durability=QoSDurabilityPolicy.VOLATILE,
		    depth=1
		)

        self.odom_subscriber = self.create_subscription(Odometry, '/odom', self._odom_callback, odom_qos_profile)
        self.yolo_subscriber = self.create_subscription(Float32MultiArray, '/yolo_data', self._yolo_callback, yolo_qos_profile)
        self.lidar_subscriber = self.create_subscription(LaserScan, '/scan', self._LIDAR_callback, lidar_qos_profile)
        self.completion_subscriber = self.create_subscription(Bool, '/teleop_completed', self._completion_callback, completion_qos_profile)
        self._objects_info_publisher = self.create_publisher(String,'/objects_info', 5)
        self._objects_info = ""
        self._angles = None
        self._ranges = None
        self.position = [0,0,0]
        # self._odom_offset = None

    # Callback to update the robot's current position
    def _odom_callback(self, odom):
        
        #x y z angle(deg)
        x = odom.pose.pose.position.x
        y = odom.pose.pose.position.y
        z_angle = odom.pose.pose.orientation.z
        self.position = [x, y, z_angle] #
        #print(self.position)

    def _yolo_callback(self, boxes):
        #ID Classification Confidence Top_left_x top_left_y bot_right_x bot_right_y
        # Process YOLO data and correlate with LIDAR data
        num_cols = 7
        bbox_array = np.array(boxes.data).reshape(-1, num_cols)
        #num_objects = bbox_array.shape[0]# Number of objects from yolo
        for row in bbox_array:
            # Translate bounding box center in pixel space to a local angle
            angle = self._pixel_to_deg((row[3] + row[5])/2)
            # Perform interpolation to get distance for detected objects
            distance = np.interp(angle, self._angles, self._ranges)
            #if len(distance) > 1:
            #    distance = distance[0]
            #TODO: Convert to string (See yolo world documentation v2)
            object_class = int(row[1])
            # ID Class Confidence x_world y_world z_world
            # Calculate world coordinates and append to objects info
            object_string = f"{int(row[0])} class:{object_class} x:{distance*math.cos(math.radians(angle + self.position[2])) + self.position[0]} y:{distance*math.sin(math.radians(angle + self.position[2])) + self.position[1]}\n" #distance:{distance} angle:{angle}\n" #TODO: Update with correct absolute coordinates
            # Concatenate string to Objects.info
            self._objects_info += object_string
        #print(self._objects_info)

    # Process LIDAR data and filter out NaN values
    def _LIDAR_callback(self, scan):
        self._angles = np.linspace(scan._angle_min, scan._angle_max, len(scan._ranges))
        self._ranges = np.array(scan.ranges)
        mask = np.logical_not(np.isnan(self._ranges))
        self._ranges = self._ranges[mask]
        self._angles = self._angles[mask]
        #print(self._ranges)

    # Publish the objects info once teleop is completed
    def _completion_callback(self, completion_status):
        if completion_status._data == True:
            # Send objects_info string to the LLMSolverPublisher
            # Concetante turtlebot position in world
            self._objects_info += f"\n-1 Turtlebot x:{self.position[0]} y:{self.position[1]} angle:{self.position[2]}\n"
            # Trim Whitespace
            stripped = self._objects_info.strip()
            msg = String()
            msg.data = stripped
            self._objects_info_publisher.publish(msg)
        #print(stripped)

    # Convert pixel position to angle in degrees
    def _pixel_to_deg(self, pixel):
        return (pixel - 160) / 160 * 31.1
    
    def _yolo_class(self, class_id):
        class_str = "human"
        return class_str

def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = ObjectsInfoPublisher()

    print("Spinning")
    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()