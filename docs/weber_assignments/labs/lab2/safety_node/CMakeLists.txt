cmake_minimum_required(VERSION 3.8)
project(safety_node)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(ackermann_msgs REQUIRED)

# C++ node: ros2 run safety_node safety_node
add_executable(safety_node src/safety_node.cpp)
ament_target_dependencies(safety_node rclcpp sensor_msgs nav_msgs ackermann_msgs)
install(TARGETS safety_node DESTINATION lib/${PROJECT_NAME})

# Python node: ros2 run safety_node safety_node.py
ament_python_install_package(${PROJECT_NAME})
install(PROGRAMS scripts/safety_node.py DESTINATION lib/${PROJECT_NAME})

ament_package()
