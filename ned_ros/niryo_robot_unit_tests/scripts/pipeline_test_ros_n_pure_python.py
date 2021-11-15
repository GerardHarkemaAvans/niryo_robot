#!/usr/bin/env python
"""
This script is made to run ROS tests on .test files
It allows to hide log which are generated by catkin's run_tests or rostest

To use it, firstly add test files names in the corresponding list, either simulation or rpi
"""
from subprocess import Popen, PIPE
import argparse

list_test_files_simulation = [
    ["niryo_robot_poses_handlers", "simulation_poses_handlers.test", False],
    ["niryo_robot_programs_manager", "simulation_programs_manager.test", False],
    ["niryo_robot_python_ros_wrapper", "simulation_python_wrapper.test", True],
]

list_test_files_rpi = [
    ["niryo_robot_poses_handlers", "rpi_poses_handlers.test", False],
    ["niryo_robot_programs_manager", "rpi_programs_manager.test", False],
    ["niryo_robot_python_ros_wrapper", "rpi_python_wrapper.test", True],
]


class Colors(object):
    """
    https://godoc.org/github.com/whitedevops/colors
    """
    # Colors
    DEFAULT = '\033[39m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    ORANGE = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = "\033[95m"

    # Font style
    BOLD = "\033[1m"

    # Reset all
    RESET = '\033[0m'


def args_parser():
    def description_parser():
        warning = 15 * '-' + " Ned Tests " + 15 * '-'
        return warning

    # def help_gripper():
    #     s = ["Run tests on gripper",
    #          "Will use Gripper 1 for simulation and Gripper 2 for Real Robot",
    #          "If not set, will test all end-effectors functions on simulation and None for the real robot"
    #          ]
    #     return "\n".join(s)

    parser = argparse.ArgumentParser(description=description_parser(),
                                     epilog=50 * '-' + '\n',
                                     # formatter_class=argparse.RawTextHelpFormatter
                                     )

    parser.add_argument("--rpi",
                        action="store_true",
                        help="If tests are done on RPI",
                        )
    parser.add_argument("--headless",
                        action="store_true",
                        help="If you want to run on headless",
                        )
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Display stderr. Nevertheless, it can be misleading"
                             "cause some errors happened when closing Gazebo",
                        )
    parser.add_argument("-gc", "--gripper_n_camera",
                        action="store_true",
                        help="Run tests also on vision node and a tool",
                        )
    parser.add_argument("--conveyor",
                        action="store_true",
                        help="Run tests with conveyor",
                        )

    l_args = parser.parse_args()
    optional_args = [
        "gripper_n_camera:={}".format(str(l_args.gripper_n_camera).lower()),
        "gui:={}".format(str(not l_args.headless).lower()),
    ]

    return l_args, optional_args


def find_result(output_clean):
    target_str = " * RESULT: "
    res = "NOT FOUND"
    for line in output_clean:
        if target_str not in line:
            continue
        res = line.replace(target_str, "")
        break
    return res.strip()


def test_pipeline(show_errors, use_simulation, optional_args=None):
    if optional_args is None:
        optional_args = []
    line = 20 * "-"
    if use_simulation:
        list_test = list_test_files_simulation
    else:
        list_test = list_test_files_rpi

    # - Display before running
    print "\n" + 20 * "*" + "\n"
    print "Executing {} tests on {} mode\n".format(
        len(list_test), Colors.BLUE + ("Simulation" if use_simulation else "RPI") + Colors.RESET)
    print "Optional args : \n{}\n".format(Colors.ORANGE + "\n".join(optional_args) + Colors.RESET)
    print "\n" + 20 * "*" + "\n"
    # - Run all commands in a loop
    list_res = []
    for dir_, file_, use_args in list_test:
        print "{}\nExecuting Test {} from Package {}".format(line, Colors.BLUE + file_ + Colors.RESET,
                                                             Colors.GREEN + dir_ + Colors.RESET)
        l_param = ["rostest", dir_, file_]
        if use_args:
            l_param.extend(optional_args)

        print "Command used : {}\n{}".format(Colors.MAGENTA + " ".join(l_param) + Colors.RESET, line)

        # Launching command in a shell and getting output
        p = Popen(l_param, stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()

        # - Analysing the output to extract only useful information which is contains after ROSTEST
        output_split = output.split("\n")
        for i in range(len(output_split)):
            if output_split[i].startswith("[ROSTEST]"):
                j = i + 1
                break
        else:
            list_res.append([dir_, file_, "{}CANNOT FIND ROSTEST RESULT{}".format(Colors.RED, Colors.RESET)])
            continue

        jump_to_end = 6  # Number of lines between "SUMMARY" on end of summary
        for j in range(i, len(output_split) - jump_to_end - 1):
            if output_split[j].startswith("SUMMARY"):
                break

        # - Format output
        output_clean_list = output_split[i + 1:j + jump_to_end + 1]
        output_clean = "\n".join(output_clean_list)

        # - Display result of the test
        if show_errors and error:
            print 3 * "!" + " Warns/Errors " + 3 * "!" + "\n"
            print error
            print 3 * "#" + " Test Results " + 3 * "#" + "\n"
        print output_clean + "\n"

        # Check if the test Succeed and store result
        list_res.append([dir_, file_, find_result(output_clean_list)])

    # - Summary of tests
    success = all(["SUCCESS" in res for _, _, res in list_res])
    if success:
        success_str = Colors.GREEN + "SUCCESS"
    else:
        success_str = Colors.RED + "FAILED"

    border = "{}--Tests Summary : {} --{}".format(Colors.BOLD, success_str + Colors.DEFAULT, Colors.RESET)
    print "\n\n" + border + "\n"

    for dir_, file_, res in list_res:
        print "File {} from package {} : {}".format(file_, dir_, res)

    print "\n" + border

    return success


if __name__ == '__main__':
    # - Getting CLI arguments
    args_, optional_args_ = args_parser()

    test_pipeline(show_errors=args_.verbose, use_simulation=not args_.rpi,
                  optional_args=optional_args_)
