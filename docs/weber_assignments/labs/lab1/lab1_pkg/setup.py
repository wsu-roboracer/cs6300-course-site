from glob import glob

from setuptools import setup

package_name = 'lab1_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # TODO (Part 3): install every file in launch/ to share/lab1_pkg/launch
        # so that `ros2 launch lab1_pkg lab1_launch.py` can find it. Use glob().
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='you@mail.weber.edu',
    description='Lab 1: a talker and a relay for AckermannDriveStamped messages',
    license='MIT',
    entry_points={
        'console_scripts': [
            # TODO (Part 1): register two executables, `talker` and `relay`,
            # that run the main() functions in talker.py and relay.py.
        ],
    },
)
