# ROS will be used to
1. receive video from robot as a ROS topic - will be used by YOLO module
2. receive lidar readings as a ROS topic - will be used by fusion module
        need to write subscriber to `sensor_msgs/laserscan.msg` : single scan from 2D Lidar.

3. receive 2D occupancy grid - will be used by fusion module
        need to write subscriber to `nav_msg/msg/OccupancyGrid` : 