import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy, QoSHistoryPolicy
from llm_script.py import LLM_Solver

from std_msgs.msg import String

class LLMSolverPublisher(Node):

    def __init__(self):
        super().__init__('example_publisher')

        qos_profile = QoSProfile(
		    reliability=QoSReliabilityPolicy.BEST_EFFORT,
		    history=QoSHistoryPolicy.KEEP_LAST,
		    durability=QoSDurabilityPolicy.VOLATILE,
		    depth=1
		)
        self._img_subscriber = self.create_subscription(String, '/object_info', self._string_callback, qos_profile)
        self._llm = LLM_Solver()
        
    def _string_callback(self, String):
        self._llm.run(String.data)


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