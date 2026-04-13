from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    video_path = LaunchConfiguration("video_path")
    model_path = LaunchConfiguration("model_path")

    return LaunchDescription([
        DeclareLaunchArgument("video_path"),
        DeclareLaunchArgument("model_path"),

        Node(
            package="detectx",
            executable="file_pub",
            name="file_pub",
            output="screen",
            parameters=[{
                "path": video_path,
                "topic": "/image",
                "fps": 15.0,
                "loop": True,
            }],
        ),

        Node(
            package="detectx",
            executable="detect_node",
            name="detectx",
            output="screen",
            parameters=[{
                "input_topic": "/image",
                "detections_topic": "/detectx/detections",
                "annotated_topic": "/detectx/annotated",
                "metrics_topic": "/detectx/metrics",
                "model_path": model_path,
                "conf": 0.25,
                "iou": 0.45,
                "device": "cpu",
                "publish_annotated": True,
                "save_video": True,
                "output_path": "/root/detectx_out/annotated.mp4",
                "output_fps": 15.0,
            }],
        ),
    ])