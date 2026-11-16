import os
from glob import glob

from setuptools import setup

package_name = 'pure_pursuit'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # TODO (Lab 6b, Part 1): install the files in config/, launch/, and maps/ to
        # share/pure_pursuit/config, share/pure_pursuit/launch, and
        # share/pure_pursuit/maps. Use os.path.join() and glob().
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='you@mail.weber.edu',
    description='Labs 6a and 6b: record waypoints and follow them with Pure Pursuit',
    license='MIT',
    entry_points={
        'console_scripts': [
            # TODO (Lab 6a, Part 2): register `waypoint_logger`, which runs
            # main() in waypoint_logger.py.
            # TODO (Lab 6b, Part 1): register `pure_pursuit_node`, which runs
            # main() in pure_pursuit_node.py.
        ],
    },
)
