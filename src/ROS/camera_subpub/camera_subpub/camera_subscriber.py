# node dependencies that have to be added to the package.xml
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2

# building the class which inherits from node class imported above
class ImageSubscriber(Node):

    def __init__(self):
        super().__init__('image_subscriber')
        self.subscription = self.create_subscription(
            Image,
            '/image_raw',
            self.listener_callback,
            10
        )
        self.subscription  # prevent unused variable warning
        self.bridge = CvBridge()  # Initialize CvBridge

    def listener_callback(self, msg):
        self.get_logger().info('Received an image')  # Log that I am seeing the image
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')  # Convert ROS Image to OpenCV image
            # You can now use OpenCV to process the cv_image
            # For example, you can display it using OpenCV:
            
            # show image
            # cv2.imshow('Received Image', cv_image)
            
            # save image
            cv2.imwrite('received_image.jpg', cv_image)  # Update the path as needed

            # cv2.waitKey(1)  # Add a small delay to allow the image to be displayed
        except CvBridgeError as e:
            self.get_logger().error('CvBridge Error: {0}'.format(e))

def main(args=None):
    rclpy.init(args=args)

    image_subscriber = ImageSubscriber()

    rclpy.spin(image_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    image_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
