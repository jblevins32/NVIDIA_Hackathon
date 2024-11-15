from setuptools import find_packages, setup

package_name = 'camera_subpub'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools','rclpy','cv_bridge','python3-opencv'],
    zip_safe=True,
    maintainer='hkwon82',
    maintainer_email='hkwon82@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'camera_publisher = camera_subpub.camera_publisher:main'
            'camera_subscriber = camera_subpub.camera_subscriber:main'
        ],
    },
)
