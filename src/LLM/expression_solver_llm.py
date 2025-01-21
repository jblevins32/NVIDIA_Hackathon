import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy, QoSHistoryPolicy
from llm_script import LLM_Solver

from std_msgs.msg import String
from std_msgs.msg import Bool

class LLMSolverPublisher(Node):

    def __init__(self):
        super().__init__('expression_solver_llm')

        qos_profile = QoSProfile(
		    reliability=QoSReliabilityPolicy.BEST_EFFORT,
		    history=QoSHistoryPolicy.KEEP_LAST,
		    durability=QoSDurabilityPolicy.VOLATILE,
		    depth=1
		)

        query_qos_profile = QoSProfile(
		    reliability=QoSReliabilityPolicy.BEST_EFFORT,
		    history=QoSHistoryPolicy.KEEP_LAST,
		    durability=QoSDurabilityPolicy.VOLATILE,
		    depth=1
		)

        self._img_subscriber = self.create_subscription(String, '/objects_info', self._string_callback, qos_profile)
        self._query_subscriber = self.create_subscription(String, '/expression_query', self._query_callback, query_qos_profile)
        self._ready_publisher = self.create_publisher(Bool, '/teleop_completed', qos_profile)
        self._query = ""

        self._llm = LLM_Solver()
        
    def _string_callback(self, String):
        self._llm.run(String.data, self._query)

    def _query_callback(self, query):
        self._query = query.data
        msg = Bool()
        msg.data = True
        self._ready_publisher.publish(msg)



def main(args=None):
    rclpy.init(args=args)

    llm_solver_publisher = LLMSolverPublisher()

    rclpy.spin(llm_solver_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    llm_solver_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()