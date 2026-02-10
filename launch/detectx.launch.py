from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_share = get_package_share_directory("detectx")
    params = os.path.join(pkg_share, "config", "detectx.yaml")

    return LaunchDescription(
        [
            Node(
                package="detectx",
                executable="detect_node",
                name="detectx",
                output="screen",
                parameters=[params],
            )
        ]
    )
