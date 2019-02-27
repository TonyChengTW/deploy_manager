#!/usr/bin/env python

from setuptools import setup, find_packages

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
    include_package_data=True,
    packages=find_packages("."),

)
