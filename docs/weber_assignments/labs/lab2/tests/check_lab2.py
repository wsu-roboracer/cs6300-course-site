#!/usr/bin/env python3
"""Score the autograded parts of Lab 2.

Build and source your workspace first, then name the language you wrote your
node in:

    python3 tests/check_lab2.py python
    python3 tests/check_lab2.py cpp

It feeds your node made-up scans and speeds, so it needs neither the simulator
nor the car. Stop your own safety node before you run it.
"""

import argparse
import math
import os
import random
import signal
import subprocess
import sys
import time

# Keep this run to itself, so other nodes on the same network cannot reach the
# topics being checked. Must be set before ROS starts.
os.environ['ROS_LOCALHOST_ONLY'] = '1'
os.environ['ROS_DOMAIN_ID'] = str(random.randint(1, 100))

try:
    import rclpy
    from ackermann_msgs.msg import AckermannDriveStamped
    from nav_msgs.msg import Odometry
    from rclpy.node import Node
    from rclpy.qos import qos_profile_sensor_data
    from sensor_msgs.msg import LaserScan
except ImportError as error:
    sys.exit(
        f'Could not import ROS 2 ({error}).\n'
        'Source ROS and install the dependencies first:\n'
        '  source /opt/ros/humble/setup.bash\n'
        '  rosdep install --from-paths src --ignore-src -y'
    )

PACKAGE = 'safety_node'
EXECUTABLES = {'python': 'safety_node.py', 'cpp': 'safety_node'}

# The scan the simulator and the car produce: 270 degrees, 1080 beams, 0 = straight ahead.
BEAMS = 1080
ANGLE_MIN = math.radians(-135)
ANGLE_INCREMENT = math.radians(270) / (BEAMS - 1)
RANGE_MAX = 30.0
ANGLES = [ANGLE_MIN + i * ANGLE_INCREMENT for i in range(BEAMS)]


# -- Scans --------------------------------------------------------------------

def wall_ahead(distance):
    """A wall across the car's path, `distance` metres in front of it."""
    return [min(distance / math.cos(a), RANGE_MAX) if abs(a) < math.pi / 2 else RANGE_MAX for a in ANGLES]


def hallway(half_width):
    """A straight hallway with a wall `half_width` metres to each side and nothing ahead."""
    return [min(half_width / abs(math.sin(a)), RANGE_MAX) if math.sin(a) else RANGE_MAX for a in ANGLES]


def object_beside(distance):
    """Open space, except for something `distance` metres directly to the car's left."""
    return [distance if abs(a - math.pi / 2) < math.radians(2) else RANGE_MAX for a in ANGLES]


def open_space():
    """Nothing in range: every beam reports inf."""
    return [math.inf] * BEAMS


def with_bad_readings(ranges):
    """The same scan with inf and nan scattered through it, as a real lidar gives."""
    noisy = list(ranges)
    for i in range(0, BEAMS, 7):
        noisy[i] = math.inf
    for i in range(3, BEAMS, 11):
        noisy[i] = math.nan
    return noisy


# -- Talking to the node ------------------------------------------------------

class Probe(Node):
    """Publishes scans and odometry, and listens for drive commands."""

    def __init__(self):
        super().__init__('lab2_check')
        self.drive = []
        self.create_subscription(
            AckermannDriveStamped, '/drive', lambda msg: self.drive.append(msg.drive), qos_profile_sensor_data)
        self.scan_publisher = self.create_publisher(LaserScan, '/scan', 10)
        self.odom_publisher = self.create_publisher(Odometry, '/ego_racecar/odom', 10)

    def spin_until(self, done, timeout):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            rclpy.spin_once(self, timeout_sec=0.02)
            if done():
                return True
        return False

    def connected(self):
        return (self.count_subscribers('/scan') > 0
                and self.count_subscribers('/ego_racecar/odom') > 0
                and self.count_publishers('/drive') > 0)

    def feed(self, ranges, speed, seconds=1.5):
        """Send this scan and speed at 20 Hz. Return True if the node braked."""
        odom = Odometry()
        odom.twist.twist.linear.x = speed
        scan = LaserScan()
        scan.header.frame_id = 'ego_racecar/laser'
        scan.angle_min = ANGLE_MIN
        scan.angle_max = ANGLES[-1]
        scan.angle_increment = ANGLE_INCREMENT
        scan.range_min = 0.0
        scan.range_max = RANGE_MAX
        scan.ranges = ranges

        self.drive.clear()
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            stamp = self.get_clock().now().to_msg()
            odom.header.stamp = scan.header.stamp = stamp
            self.odom_publisher.publish(odom)
            self.scan_publisher.publish(scan)
            self.spin_until(lambda: False, 0.05)
        return any(abs(command.speed) < 1e-3 for command in self.drive)


class StudentNode:
    """Runs the student's safety node for the length of a `with` block."""

    def __init__(self, probe, executable):
        self.probe = probe
        self.executable = executable

    def __enter__(self):
        self.process = subprocess.Popen(
            ['ros2', 'run', PACKAGE, self.executable],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        self.connected = self.probe.spin_until(
            lambda: self.probe.connected() or self.process.poll() is not None, 10) and self.probe.connected()
        return self

    def alive(self):
        return self.process.poll() is None

    def __exit__(self, *exc):
        if self.alive():
            os.killpg(self.process.pid, signal.SIGINT)
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(self.process.pid, signal.SIGKILL)
                self.process.wait()
        # Let the stopped node drop off the ROS graph before the next one starts.
        self.probe.spin_until(lambda: not self.probe.connected(), 5)


# -- Checks -------------------------------------------------------------------
# Each scenario starts a fresh copy of the node, so a brake that stays on after
# one scenario cannot affect the next.

def check_starts(probe, executable, state):
    result = subprocess.run(['ros2', 'pkg', 'executables', PACKAGE], capture_output=True, text=True)
    if executable not in {line.split()[-1] for line in result.stdout.splitlines() if line.strip()}:
        return False, f'`ros2 run {PACKAGE} {executable}` does not exist; build and source your workspace'
    with StudentNode(probe, executable) as node:
        if not node.alive():
            return False, 'the node exited as soon as it started'
        if not node.connected:
            return False, 'the node must subscribe to /scan and /ego_racecar/odom and publish on /drive'
    state['starts'] = True
    return True, ''


def scenario(ranges, speed, should_brake, what, needs_braking=False):
    """Build a check that feeds one scan and speed and expects braking or no braking."""
    def check(probe, executable, state):
        if not state.get('starts'):
            return False, 'the node has to start and connect first'
        if needs_braking and not state.get('brakes'):
            return False, 'counted only once the node brakes for a wall ahead'
        with StudentNode(probe, executable) as node:
            braked = probe.feed(ranges, speed)
            if not node.alive():
                return False, f'the node crashed: {what}'
        if braked != should_brake:
            return False, f'{"did not brake" if should_brake else "braked"}: {what}'
        if should_brake:
            state['brakes'] = True
        return True, ''
    return check


CHECKS = [
    ('Compilation', [
        (30, 'builds, starts, and connects to its three topics', check_starts),
    ]),
    ('Stops before collision', [
        (15, 'brakes for a wall ahead',
         scenario(wall_ahead(0.5), 2.5, True, 'wall 0.5 m ahead at 2.5 m/s, 0.2 s to collision')),
        (15, 'brakes when the scan contains inf and nan',
         scenario(with_bad_readings(wall_ahead(0.5)), 2.5, True,
                  'wall 0.5 m ahead at 2.5 m/s, with inf and nan readings in the scan')),
    ]),
    ('Calculates TTC', [
        (4, 'brakes for a far wall at high speed',
         scenario(wall_ahead(2.0), 10.0, True, 'wall 2.0 m ahead at 10 m/s, 0.2 s to collision')),
        (3, 'does not brake for a near wall at low speed',
         scenario(wall_ahead(1.0), 0.25, False, 'wall 1.0 m ahead at 0.25 m/s, 4 s to collision', True)),
        (3, 'does not brake for something beside the car',
         scenario(object_beside(0.4), 2.5, False,
                  'object 0.4 m directly to the left at 2.5 m/s; the car is not closing on it', True)),
    ]),
    ('Navigates the hallway', [
        (5, 'does not brake in a straight hallway',
         scenario(hallway(1.5), 1.0, False, 'walls 1.5 m to each side, nothing ahead, at 1.0 m/s', True)),
        (5, 'does not brake in open space',
         scenario(open_space(), 2.5, False, 'every beam reads inf, at 2.5 m/s', True)),
    ]),
]


def main():
    parser = argparse.ArgumentParser(description='Score the autograded parts of Lab 2.')
    parser.add_argument('language', choices=sorted(EXECUTABLES), help='the language you wrote your node in')
    args = parser.parse_args()
    executable = EXECUTABLES[args.language]

    rclpy.init()
    probe = Probe()
    state = {}
    score = total = 0
    print(f'Checking: ros2 run {PACKAGE} {executable}')
    for part, checks in CHECKS:
        print(f'\n{part}')
        for points, name, check in checks:
            passed, detail = check(probe, executable, state)
            total += points
            score += points if passed else 0
            print(f'  [{"PASS" if passed else "FAIL"}] {points if passed else 0:>2}/{points:<2}  {name}')
            if detail:
                print(f'                  {detail}')
    probe.destroy_node()
    rclpy.try_shutdown()

    print(f'\nAutograded score: {score}/{total}')
    print('The video is worth 20 more points and is graded by hand.')
    return 0 if score == total else 1


if __name__ == '__main__':
    sys.exit(main())
