# node dependencies that have to be added to the package.xml
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

# building the class which inherits from node class imported above
class ImagePublisher(Node):

    def __init__(self):
        super().__init__('image_publisher') # function from the node class that is a constructor. Unsure what it does.
        self.publisher_ = self.create_publisher(Image, '/image_raw', 10) # declare that this node publishes images over a topic \iamge_raw with a queue of 10. Must match subscriber!!
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback) # creating a timer to call the timer_callback at a specific interval
        self.bridge = CvBridge() # bridges the gap between ROS images and OpenCV images
        self.cap = cv2.VideoCapture(0) # create a video capture object for camera 0

    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret: # Check if an image has been successfully captured
            msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8') # convert cv2 to ROS image
            self.publisher_.publish(msg) # publish the message
            self.get_logger().info('Publishing Image') # Log that I am publishing the image
            
    def destroy(self):
        self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)

    image_publisher = ImagePublisher() # define an instance of image publisher class

    rclpy.spin(image_publisher) # run the node

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    image_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
