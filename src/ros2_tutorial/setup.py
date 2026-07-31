from setuptools import setup
import os
from glob import glob

package_name = 'ros2_tutorial'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name), glob('launch/*.*'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='manel.puig@ub.edu',
    description='TODO: Package description',
    license='TODO: License declaration',
    entry_points={
        'console_scripts': [
            'publisher_exec = ros2_tutorial.publisher_hello:main',
            'subscriber_exec = ros2_tutorial.subscriber_hello:main',
        ],
    },
)
