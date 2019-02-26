#!/usr/bin/env python

from setuptools import setup

setup(
    name='deploy_manager',
    version='1.0.0',
    description=('deploy_manager'),
    long_description='deploy pxe manager for changing IP and hostname',
    license='Apache v2',
    classifiers=[
        'Programming Language :: Python :: 2.7',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'deploy_manager = deploy_manager.app.server:launch'
        ],
        'ip_manager.drivers': [
            'ipv4 = ip_manager_v1.driver:Driver'
        ],
        'hostname_manager.drivers': [
            'hostname = hostname_manager_v1.driver:Driver'
        ],
        'upgrade_manager.drivers': [
            'apt_package = upgrade_manager_v1.driver:Driver'
        ]
    },
)
