# node dependencies that NNED to be added to the package.xml
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32MultiArray
from cv_bridge import CvBridge, CvBridgeError
from yolo_pubsub.yolo_world_ROS import yolo_cls
import numpy as np

# building the class which inherits from ROS2 node class
class ImageSubscriber(Node):
    '''
    This node:
    1) subscribes to the image_data topic
    2) converts the image to readable format
    3) runs the yolo model on the image for tracking
    4) stores detected object data
    '''
    
    def __init__(self):
        super().__init__('image_subscriber') # ROS node identifier, given the name of the node
        
        # Subscribe to image data topic
        self.subscription = self.create_subscription(
            Image, # message type
            'image_raw', # topic name
            self.listener_callback, # function to execute when the node receives a message on this topic
            10 # Queue size
        )
        
        self.publisher_data = self.create_publisher(Float32MultiArray, '/yolo_data', 10) # declare that this node publishes images over a topic \image_raw with a queue of 10. Must match subscriber!!
        self.publisher_img = self.create_publisher(Image, '/yolo_img', 10) # declare that this node publishes images over a topic \image_raw with a queue of 10. Must match subscriber!!
                            
        # initialize object for converting ROS img messages to viewable CV messages
        self.bridge = CvBridge()
        
        # Initialize YOLO model
        self.yolo_obj = yolo_cls()
        
    def listener_callback(self,msg):
        # Log a message that image is received
        self.get_logger().info('Received an image')
        
        # Main operations and data collection from the received images... call yolo here
        try:
            # Convert ROS image to OpenCV image
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8') 
            
            # Run tracking and data logging on image
            yolo_data, img = self.yolo_obj.YOLOrun(cv_image)
            data_msg = Float32MultiArray()
            data_msg.data = yolo_data.flatten().tolist()
            print(data_msg.data)
            ros_img = self.bridge.cv2_to_imgmsg(img, encoding="bgr8")
            
            # Publish the data
            self.publisher_data.publish(data_msg) # publish the message
            self.publisher_img.publish(ros_img) # publish the image
            self.get_logger().info('Publishing Yolo Data') # Log that I am publishing the image
            

            # save image
            # cv2.imwrite('received_image.jpg', cv_image)  # Update this path

        # Display error message if no image is gather
        except CvBridgeError as e:
            self.get_logger().error('CvBridge Error: {0}'.format(e))
            
def main(args=None):
    rclpy.init(args=args)
    
    image_subscriber = ImageSubscriber()
    
    rclpy.spin(image_subscriber)
    
    image_subscriber.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()