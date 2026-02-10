from __future__ import annotations

from typing import List

import cv2
import numpy as np
import rclpy
from rclpy.node import Node

from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose, BoundingBox2D

from .model import YoloV8Detector, Detection


class DetectXNode(Node):
    def __init__(self) -> None:
        super().__init__("detectx")

        self.declare_parameter("input_topic", "/image")
        self.declare_parameter("detections_topic", "/detectx/detections")
        self.declare_parameter("annotated_topic", "/detectx/annotated")
        self.declare_parameter("model_path", "yolov8n.pt")
        self.declare_parameter("conf", 0.25)
        self.declare_parameter("iou", 0.45)
        self.declare_parameter("device", "cpu")
        self.declare_parameter("publish_annotated", True)

        input_topic = self.get_parameter("input_topic").get_parameter_value().string_value
        det_topic = self.get_parameter("detections_topic").get_parameter_value().string_value
        ann_topic = self.get_parameter("annotated_topic").get_parameter_value().string_value

        model_path = self.get_parameter("model_path").get_parameter_value().string_value
        conf = self.get_parameter("conf").get_parameter_value().double_value
        iou = self.get_parameter("iou").get_parameter_value().double_value
        device = self.get_parameter("device").get_parameter_value().string_value
        self._publish_annotated = self.get_parameter("publish_annotated").get_parameter_value().bool_value

        self._bridge = CvBridge()
        self._detector = YoloV8Detector(model_path=model_path, conf=conf, iou=iou, device=device)

        self._sub = self.create_subscription(Image, input_topic, self._on_image, 10)
        self._pub_det = self.create_publisher(Detection2DArray, det_topic, 10)
        self._pub_ann = self.create_publisher(Image, ann_topic, 10) if self._publish_annotated else None

        self.get_logger().info(f"DetectX started. input={input_topic} detections={det_topic}")

    def _on_image(self, msg: Image) -> None:
        try:
            bgr = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f"cv_bridge failed: {e}")
            return

        dets = self._detector.infer_bgr(bgr)
        self._pub_det.publish(self._to_detection2d_array(msg, dets))

        if self._pub_ann is not None:
            ann = self._draw(bgr, dets)
            ann_msg = self._bridge.cv2_to_imgmsg(ann, encoding="bgr8")
            ann_msg.header = msg.header
            self._pub_ann.publish(ann_msg)

    def _to_detection2d_array(self, img_msg: Image, dets: List[Detection]) -> Detection2DArray:
        out = Detection2DArray()
        out.header = img_msg.header

        for d in dets:
            x1, y1, x2, y2 = d.xyxy
            w = max(0.0, x2 - x1)
            h = max(0.0, y2 - y1)
            cx = x1 + 0.5 * w
            cy = y1 + 0.5 * h

            det2d = Detection2D()
            det2d.bbox = BoundingBox2D()
            det2d.bbox.center.position.x = float(cx)
            det2d.bbox.center.position.y = float(cy)
            det2d.bbox.size_x = float(w)
            det2d.bbox.size_y = float(h)

            hyp = ObjectHypothesisWithPose()
            hyp.hypothesis.class_id = str(d.cls_id)
            hyp.hypothesis.score = float(d.conf)

            det2d.results.append(hyp)
            out.detections.append(det2d)

        return out

    def _draw(self, bgr: np.ndarray, dets: List[Detection]) -> np.ndarray:
        img = bgr.copy()
        for d in dets:
            x1, y1, x2, y2 = map(int, d.xyxy)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{d.cls_name} {d.conf:.2f}"
            cv2.putText(img, label, (x1, max(0, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return img


def main() -> None:
    rclpy.init()
    node = DetectXNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
