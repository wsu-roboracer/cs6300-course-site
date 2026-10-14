#!/usr/bin/env python3
"""Score the autograded parts of Lab 1.

Build and source your workspace first, then run this from anywhere:

    python3 tests/check_lab1.py

It starts your nodes, so stop any talker, relay, or launch file you have
running before you run it.
"""

import os
import random
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

# Keep this run to itself, so a classmate's nodes on the same network cannot
# reach the topics being checked. Must be set before ROS starts.
os.environ['ROS_LOCALHOST_ONLY'] = '1'
os.environ['ROS_DOMAIN_ID'] = str(random.randint(1, 100))

try:
    import rclpy
    from ackermann_msgs.msg import AckermannDriveStamped
    from rclpy.node import Node
except ImportError as error:
    sys.exit(
        f'Could not import ROS 2 ({error}).\n'
        'Source ROS and install the dependencies first:\n'
        '  source /opt/ros/humble/setup.bash\n'
        '  rosdep install --from-paths src --ignore-src -y'
    )

PACKAGE = 'lab1_pkg'
PACKAGE_XML = Path(__file__).resolve().parents[1] / PACKAGE / 'package.xml'


class Probe(Node):
    """Listens on both topics and can publish on `drive`."""

    def __init__(self):
        super().__init__('lab1_check')
        self.seen = {'drive': [], 'drive_relay': []}
        for topic in self.seen:
            self.create_subscription(
                AckermannDriveStamped, topic, lambda msg, topic=topic: self.seen[topic].append(msg.drive), 10)
        self.publisher = self.create_publisher(AckermannDriveStamped, 'drive', 10)

    def spin_until(self, done, timeout):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            rclpy.spin_once(self, timeout_sec=0.05)
            if done():
                return True
        return False

    def clear(self):
        """Drop anything still arriving from a node that was just stopped."""
        self.spin_until(lambda: False, 0.5)
        for messages in self.seen.values():
            messages.clear()


def start(*command):
    return subprocess.Popen(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def stop(process):
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGINT)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()


def close(a, b):
    return abs(a - b) < 1e-3


def package_prefix():
    result = subprocess.run(['ros2', 'pkg', 'prefix', PACKAGE], capture_output=True, text=True)
    return Path(result.stdout.strip()) if result.returncode == 0 else None


# -- Part 1 -------------------------------------------------------------------

def check_dependency(probe):
    declared = {
        element.text.strip()
        for element in ET.parse(PACKAGE_XML).getroot()
        if element.tag in ('depend', 'exec_depend') and element.text
    }
    if 'ackermann_msgs' in declared:
        return True, ''
    return False, 'package.xml does not declare ackermann_msgs'


def check_executables(probe):
    result = subprocess.run(['ros2', 'pkg', 'executables', PACKAGE], capture_output=True, text=True)
    found = {line.split()[-1] for line in result.stdout.splitlines() if line.strip()}
    missing = {'talker', 'relay'} - found
    if missing:
        return False, f'not registered in setup.py: {", ".join(sorted(missing))}'
    return True, ''


# -- Part 2 -------------------------------------------------------------------

def check_talker(probe):
    talker = start('ros2', 'run', PACKAGE, 'talker', '--ros-args', '-p', 'v:=1.5', '-p', 'd:=0.25')
    try:
        drive = probe.seen['drive']
        if not probe.spin_until(lambda: len(drive) >= 5 or talker.poll() is not None, 10) or len(drive) < 5:
            return False, 'nothing was published on `drive`'
        if not (close(drive[-1].speed, 1.5) and close(drive[-1].steering_angle, 0.25)):
            return False, (
                f'with v=1.5 and d=0.25, got speed={drive[-1].speed:.3f} '
                f'and steering_angle={drive[-1].steering_angle:.3f}'
            )
        drive.clear()
        probe.spin_until(lambda: False, 1.0)
        if len(drive) < 50:
            return False, f'only {len(drive)} messages in one second; publish from a 0.001 second timer'
        return True, ''
    finally:
        stop(talker)
        probe.clear()


def check_talker_param_change(probe):
    talker = start('ros2', 'run', PACKAGE, 'talker', '--ros-args', '-p', 'v:=1.5', '-p', 'd:=0.25')
    try:
        drive = probe.seen['drive']
        if not probe.spin_until(lambda: len(drive) >= 5 or talker.poll() is not None, 10) or len(drive) < 5:
            return False, 'nothing was published on `drive`'
        subprocess.run(['ros2', 'param', 'set', '/talker', 'v', '2.5'], capture_output=True, timeout=30)
        if probe.spin_until(lambda: close(drive[-1].speed, 2.5), 5):
            return True, ''
        return False, 'after `ros2 param set /talker v 2.5` the speed did not change'
    except subprocess.TimeoutExpired:
        return False, '`ros2 param set /talker v 2.5` did not finish'
    finally:
        stop(talker)
        probe.clear()


def check_relay(probe):
    relay = start('ros2', 'run', PACKAGE, 'relay')
    try:
        command = AckermannDriveStamped()
        command.drive.speed = 2.0
        command.drive.steering_angle = 0.1
        relayed = probe.seen['drive_relay']

        def publish_and_check():
            probe.publisher.publish(command)
            return bool(relayed) or relay.poll() is not None

        if not probe.spin_until(publish_and_check, 10) or not relayed:
            return False, 'nothing was published on `drive_relay`'
        if not (close(relayed[-1].speed, 6.0) and close(relayed[-1].steering_angle, 0.3)):
            return False, (
                f'sent speed=2.0 and steering_angle=0.1, got speed={relayed[-1].speed:.3f} '
                f'and steering_angle={relayed[-1].steering_angle:.3f}'
            )
        return True, ''
    finally:
        stop(relay)
        probe.clear()


# -- Part 3 -------------------------------------------------------------------

def check_launch_installed(probe):
    if (package_prefix() / 'share' / PACKAGE / 'launch' / 'lab1_launch.py').is_file():
        return True, ''
    return False, 'lab1_launch.py is not installed; add the launch folder to data_files in setup.py and rebuild'


def check_launch(probe):
    launch = start('ros2', 'launch', PACKAGE, 'lab1_launch.py')
    try:
        drive, relayed = probe.seen['drive'], probe.seen['drive_relay']
        if not probe.spin_until(lambda: (drive and relayed) or launch.poll() is not None, 15) or not (drive and relayed):
            quiet = [topic for topic, messages in probe.seen.items() if not messages]
            return False, f'after launching, nothing was published on: {", ".join(quiet)}'
        names = set(probe.get_node_names())
        missing = {'talker', 'relay'} - names
        if missing:
            return False, f'node not running under the expected name: {", ".join(sorted(missing))}'
        if not (close(relayed[-1].speed, 3 * drive[-1].speed)
                and close(relayed[-1].steering_angle, 3 * drive[-1].steering_angle)):
            return False, '`drive_relay` is not 3 times `drive`'
        return True, ''
    finally:
        stop(launch)
        probe.clear()


CHECKS = [
    ('Part 1: Package', [
        (10, 'package.xml declares ackermann_msgs', check_dependency),
        (15, 'talker and relay executables are registered', check_executables),
    ]),
    ('Part 2: Nodes', [
        (10, 'talker publishes v and d on `drive`', check_talker),
        (5, 'talker picks up a parameter change', check_talker_param_change),
        (10, 'relay publishes 3 times the command on `drive_relay`', check_relay),
    ]),
    ('Part 3: Launch file', [
        (10, 'lab1_launch.py is installed', check_launch_installed),
        (15, 'lab1_launch.py starts both nodes', check_launch),
    ]),
]


def main():
    if package_prefix() is None:
        sys.exit(
            f'ROS cannot find {PACKAGE}. Build and source your workspace first:\n'
            '  colcon build --packages-select lab1_pkg\n'
            '  source install/setup.bash'
        )

    rclpy.init()
    probe = Probe()
    score = total = 0
    for part, checks in CHECKS:
        print(f'\n{part}')
        for points, name, check in checks:
            passed, detail = check(probe)
            total += points
            score += points if passed else 0
            print(f'  [{"PASS" if passed else "FAIL"}] {points if passed else 0:>2}/{points:<2}  {name}')
            if detail:
                print(f'                  {detail}')
    probe.destroy_node()
    rclpy.try_shutdown()

    print(f'\nAutograded score: {score}/{total}')
    print('The written questions in SUBMISSION.md are worth 25 more points and are graded by hand.')
    return 0 if score == total else 1


if __name__ == '__main__':
    sys.exit(main())
