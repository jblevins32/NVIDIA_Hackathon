# node dependencies that NNED to be added to the package.xml
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from yolo_world_ROS import yolo

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
            'image_data', # topic name
            self.listener_callback, # function to execute when the node receives a message on this topic
            10 # Queue size
        )
        
        # initialize object for converting ROS img messages to viewable CV messages
        self.bridge = CvBridge()
        
        # Initialize YOLO model
        self.yolo_obj = yolo
        
    def listener_callback(self,msg):
        # Log a message that image is received
        self.get_logger().info('Received an image')
        
        # Main operations and data collection from the received images... call yolo here
        try:
            # Convert ROS image to OpenCV image
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8') 
            
            # Run tracking and data logging on image
            self.yolo_obj.YOLOrun(cv_image)
            
            # save image
            # cv2.imwrite('received_image.jpg', cv_image)  # Update this path

        # Display error message if no image is gather
        except CvBridgeError as e:
            self.get_logger().error('CvBridge Error: {0}'.format(e))
            
def main(args=None):
    rclpy.init(args=args)
    
    image_subscriber = ImageSubscriber()
    
    rclpy.sim(image_subscriber)
    
    image_subscriber.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()