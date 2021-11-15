from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['niryo_robot_user_interface'],
    # scripts=['bin/myscript'],
    package_dir={'': 'src'}
)

setup(**d)
