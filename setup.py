#!/usr/bin/env python

from setuptools import setup

setup(
    name='cc-iaas-sdnms',
    version='1.0.0',
    description=('cc-iaas-sdnms'),
    long_description='cc-iaas-sdnms',
    license='Apache v2',
    classifiers=[
        'Programming Language :: Python :: 2.7',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'cc-iaas-sdnms = cc_iaas_sdnms.app.server:launch'
        ],
        'backend.fw.drivers': [
            'fw_fortinet_v5_6_3 = fw_fortinet_v5_6_3.driver:Driver'
        ],
        'backend.waf.drivers': [
            'waf_f5_v13_1 = waf_f5_v13_1.driver:Driver'
        ],
        'backend.switch.drivers': [
            'sw_mellanox_sn2410 = sw_mellanox_sn2410.driver:Driver'
        ]
    },
)
