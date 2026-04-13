from setuptools import setup

package_name = "detectx"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", [
    "launch/detectx.launch.py",
    "launch/detectx_demo.launch.py",
]),
        ("share/" + package_name + "/config", ["config/detectx.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="root",
    maintainer_email="lorinitzhak284@gmail.com",
    description="DetectX: YOLOv8 object detection node for ROS2",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
    "detect_node = detectx.detect_node:main",
    "file_pub = detectx.file_pub:main",
],

    },
)
