import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy, QoSHistoryPolicy

from std_msgs.msg import String

class LLMQueryPublisher(Node):

    def __init__(self):
        super().__init__('llm_query_publisher')

        query_qos_profile = QoSProfile(
		    reliability=QoSReliabilityPolicy.BEST_EFFORT,
		    history=QoSHistoryPolicy.KEEP_LAST,
		    durability=QoSDurabilityPolicy.VOLATILE,
		    depth=1
		)

        self._query_publisher = self.create_publisher(String, '/expression_query', query_qos_profile)
        
    def publish_query(self, query):
        msg = String()
        msg.data = query
        self._query_publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    llm_query_publisher = LLMQueryPublisher()

    try:
        while rclpy.ok():
            rclpy.spin_once(llm_query_publisher, timeout_sec=0.1)
            user_input = input("Enter your expression query (type 'exit' or 'quit' to exit): ")
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting the node.")
                break
            llm_query_publisher.publish_query(user_input)
    except KeyboardInterrupt:
        print("Node interrupted by user.")
    finally:
        # Destroy the node explicitly
        # (optional - otherwise it will be done automatically
        # when the garbage collector destroys the node object)
        llm_query_publisher.destroy_node()
        rclpy.shutdown()
    

if __name__ == '__main__':
    main()