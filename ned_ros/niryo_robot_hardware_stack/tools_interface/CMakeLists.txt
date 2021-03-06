cmake_minimum_required(VERSION 2.8.3)
project(tools_interface)
message("\n## Reading ${PROJECT_NAME}/CMakeLists.txt...")

## Compile as C++11, supported in ROS Kinetic and newer
add_compile_options(-std=c++11)

find_package(catkin REQUIRED
    COMPONENTS
        dynamixel_driver
        message_generation
        roscpp
        std_msgs
)

find_package(Boost REQUIRED COMPONENTS system)

add_service_files(
  DIRECTORY
    srv
  FILES
    CloseGripper.srv
    OpenGripper.srv
    PingDxlTool.srv
    PullAirVacuumPump.srv
    PushAirVacuumPump.srv
)

generate_messages(
  DEPENDENCIES
    std_msgs
)

catkin_package(
    INCLUDE_DIRS
        include
    LIBRARIES
        ${PROJECT_NAME}
    CATKIN_DEPENDS
        dynamixel_driver
        message_runtime
        roscpp
        std_msgs
)

###########
## Build ##
###########

## Specify additional locations of header files
## Your package locations should be listed before other locations

include_directories(
    include
    ${catkin_INCLUDE_DIRS}
)

add_library(${PROJECT_NAME}
    src/tool_state.cpp
    src/${PROJECT_NAME}_core.cpp
)

add_executable(${PROJECT_NAME}_node
  src/${PROJECT_NAME}_node.cpp
)

## Add dependencies to exported targets, like ROS msgs or srvs
add_dependencies(${PROJECT_NAME}_node
  ${catkin_EXPORTED_TARGETS}
)

add_dependencies(${PROJECT_NAME} 
  ${PROJECT_NAME}_generate_messages_cpp
)
add_dependencies(${PROJECT_NAME} 
  dynamixel_driver_generate_messages_cpp
)

## Specify libraries to link executable targets against
target_link_libraries(${PROJECT_NAME}
  ${catkin_LIBRARIES}
)

target_link_libraries(${PROJECT_NAME}_node
  ${PROJECT_NAME}
)

#############
## Install ##
#############

install(
  TARGETS ${PROJECT_NAME}
  ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  RUNTIME DESTINATION ${CATKIN_GLOBAL_BIN_DESTINATION}
)

install(
  TARGETS ${PROJECT_NAME}_node
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

# Mark other files for installation
install(
  DIRECTORY include/${PROJECT_NAME}/
  DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
)

##########################
## Static code analysis ##
##########################

find_package(roslint QUIET)

if(roslint_FOUND)
    roslint_cpp()
else()
    message(WARNING "roslint not found. Skipping roslint target building")
endif()
