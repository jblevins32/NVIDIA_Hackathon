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
        super().__init__('objects_info_publisher')

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
        self._objects_info_string = ""
        self._objects_info = np.empty((0,5))
        self._angles = None
        self._ranges = None
        self.position = [0,0,0]
        
    # Callback to update the robot's current position
    def _odom_callback(self, odom):
        x = odom.pose.pose.position.x
        y = odom.pose.pose.position.y
        z_angle = odom.pose.pose.orientation.z
        self.position = [x, y, z_angle] #
        #print(self.position)

    def _yolo_callback(self, boxes):
        if self._angles is None:
            return
        #ID Classification Confidence Top_left_x top_left_y bot_right_x bot_right_y
        # Process YOLO data and correlate with LIDAR data
        num_cols = 7
        bbox_array = np.array(boxes.data).reshape(-1, num_cols)
        #num_objects = bbox_array.shape[0]# Number of objects from yolo
        for row in bbox_array:
            obj_id = int(row[0])
            # Translate bounding box center in pixel space to a local angle
            angle = self._pixel_to_deg((row[3] + row[5])/2)
            # Perform interpolation to get distance for detected objects
            distance = np.interp(angle, self._angles, self._ranges)
            #Convert class id to string
            object_class = self._yolo_class(int(row[1]))
            # ID Class Confidence x_world y_world z_world
            # Calculate world coordinates and append to objects info
            x = distance*math.cos(math.radians(angle) + self.position[2]) + self.position[0]
            y = distance*math.sin(math.radians(angle) + self.position[2]) + self.position[1]
            new_object = np.array([row[0], row[1], row[2], x, y])
            duplicate_found = False
            for obj in self._objects_info:
                if obj[1] == row[1]: #Check if same class
                    threshold = 0.03 #Threshold distance in meters
                    duplicate_distance = np.sqrt((x - obj[3])**2 + (y - obj[4])**2)
                    if duplicate_distance <= threshold:
                        if row[2] > obj[2]:
                            obj[2] = row[2]
                        duplicate_found = True
                        break
            if duplicate_found:
                continue
            self._objects_info = np.vstack((self._objects_info, new_object))
            object_string = f"id:{obj_id} class:{object_class} confidence:{row[2]} x:{x} y:{y}\n"
            self._objects_info_string += object_string

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
            final_string = self._objects_info_string
            final_string += f"\nid:-1 class:Turtlebot x:{self.position[0]} y:{self.position[1]} angle:{self.position[2]}\n"
            # Trim Whitespace
            stripped = final_string.strip()
            msg = String()
            msg.data = stripped
            self._objects_info_publisher.publish(msg)
        #print(stripped)

    # Convert pixel position to angle in degrees
    def _pixel_to_deg(self, pixel):
        return (pixel - 0.5) * 54 #Pi Camera v1 is 54degree angle of view
    
    def _yolo_class(self, class_id):
        class_dict = {
            0: "person",
            1: "bicycle",
            2: "car",
            3: "motorcycle",
            4: "airplane",
            5: "bus",
            6: "train",
            7: "truck",
            8: "boat",
            9: "traffic light",
            10: "fire hydrant",
            11: "stop sign",
            12: "parking meter",
            13: "bench",
            14: "bird",
            15: "cat",
            16: "dog",
            17: "horse",
            18: "sheep",
            19: "cow",
            20: "elephant",
            21: "bear",
            22: "zebra",
            23: "giraffe",
            24: "backpack",
            25: "umbrella",
            26: "handbag",
            27: "tie",
            28: "suitcase",
            29: "frisbee",
            30: "skis",
            31: "snowboard",
            32: "sports ball",
            33: "kite",
            34: "baseball bat",
            35: "baseball glove",
            36: "skateboard",
            37: "surfboard",
            38: "tennis racket",
            39: "bottle",
            40: "wine glass",
            41: "cup",
            42: "fork",
            43: "knife",
            44: "spoon",
            45: "bowl",
            46: "banana",
            47: "apple",
            48: "sandwich",
            49: "orange",
            50: "broccoli",
            51: "carrot",
            52: "hot dog",
            53: "pizza",
            54: "donut",
            55: "cake",
            56: "chair",
            57: "couch",
            58: "potted plant",
            59: "bed",
            60: "dining table",
            61: "toilet",
            62: "tv",
            63: "laptop",
            64: "mouse",
            65: "remote",
            66: "keyboard",
            67: "cell phone",
            68: "microwave",
            69: "oven",
            70: "toaster",
            71: "sink",
            72: "refrigerator",
            73: "book",
            74: "clock",
            75: "vase",
            76: "scissors",
            77: "teddy bear",
            78: "hair drier",
            79: "toothbrush",
        }
        class_str = class_dict[class_id]
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