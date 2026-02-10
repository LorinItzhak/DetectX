from __future__ import annotations

import cv2
import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image


class FileImagePublisher(Node):
    def __init__(self) -> None:
        super().__init__("file_image_publisher")

        self.declare_parameter("path", "")
        self.declare_parameter("topic", "/image")
        self.declare_parameter("fps", 15.0)
        self.declare_parameter("loop", True)

        path = self.get_parameter("path").get_parameter_value().string_value
        topic = self.get_parameter("topic").get_parameter_value().string_value
        fps = self.get_parameter("fps").get_parameter_value().double_value
        self._loop = self.get_parameter("loop").get_parameter_value().bool_value

        if not path:
            raise RuntimeError("Parameter 'path' is required")

        self._cap = cv2.VideoCapture(path)
        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open file: {path}")

        self._pub = self.create_publisher(Image, topic, 10)
        self._bridge = CvBridge()

        period = 1.0 / max(1.0, fps)
        self.create_timer(period, self._tick)

        self.get_logger().info(f"Publishing '{path}' to topic '{topic}' at {fps} FPS")

    def _tick(self) -> None:
        ok, frame = self._cap.read()
        if not ok:
            if self._loop:
                self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                return
            self.get_logger().info("EOF reached. Stopping.")
            rclpy.shutdown()
            return

        msg = self._bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        self._pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = FileImagePublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
