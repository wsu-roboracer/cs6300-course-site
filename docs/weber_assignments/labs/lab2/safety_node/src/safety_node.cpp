// Lab 2: brake the car when a collision is imminent.

#include <cmath>
#include <functional>
#include <limits>
#include <memory>

#include "ackermann_msgs/msg/ackermann_drive_stamped.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"

// Handles emergency braking.
class Safety : public rclcpp::Node
{
public:
  Safety()
  : Node("safety_node")
  {
    // TODO: create a publisher for AckermannDriveStamped messages on /drive

    // TODO: subscribe to /scan (LaserScan) with scan_callback

    // TODO: subscribe to /ego_racecar/odom (Odometry) with odom_callback
  }

private:
  // The car's current longitudinal speed in m/s, updated by odom_callback.
  double speed_ = 0.0;

  // TODO: declare your publisher and your two subscribers here

  void odom_callback(const nav_msgs::msg::Odometry::ConstSharedPtr odom_msg)
  {
    // TODO: store the car's speed. It is the x component of the linear
    // velocity: odom_msg->twist.twist.linear.x
    (void)odom_msg;  // delete this line once you use odom_msg
  }

  void scan_callback(const sensor_msgs::msg::LaserScan::ConstSharedPtr scan_msg)
  {
    // TODO: work out the angle of every beam from scan_msg->angle_min and
    // scan_msg->angle_increment. Angle 0 is straight ahead.

    // TODO: calculate the iTTC of every beam: the range divided by how fast
    // the car is closing on that beam, speed * cos(angle). A beam the car is
    // not closing on has no time to collision.

    // TODO: ignore readings that are inf or nan

    // TODO: if the smallest iTTC is below your threshold, publish an
    // AckermannDriveStamped message with drive.speed set to 0.0 to brake
    (void)scan_msg;  // delete this line once you use scan_msg
  }
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Safety>());
  rclcpp::shutdown();
  return 0;
}
