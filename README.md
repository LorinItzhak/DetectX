# DetectX

Real-time object detection pipeline built with **ROS 2**, **Python**, **YOLOv8**, **PyTorch**, and **OpenCV**.

DetectX ingests image frames from a ROS 2 topic, runs YOLOv8 inference, publishes detections and annotated frames, and reports runtime metrics such as FPS and inference latency.

## Features

- Subscribes to a ROS 2 image stream on `/image`
- Runs YOLOv8 inference on each frame
- Publishes detections to `/detectx/detections`
- Publishes annotated images to `/detectx/annotated`
- Publishes runtime metrics to `/detectx/metrics`
- Saves annotated output video to disk

## Tech Stack

- ROS 2 Humble
- Python
- Ultralytics YOLOv8
- PyTorch
- OpenCV
- cv_bridge
- vision_msgs

## Project Structure

```bash
detectx/
├── config/
│   └── detectx.yaml
├── detectx/
│   ├── detect_node.py
│   ├── file_pub.py
│   └── model.py
├── launch/
│   ├── detectx.launch.py
│   └── detectx_demo.launch.py
├── resource/
├── package.xml
├── setup.py
└── README.md