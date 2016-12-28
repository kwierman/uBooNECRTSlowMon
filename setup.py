#!/usr/bin/env python
from setuptools import find_packages
from distutils.core import setup
from pip.req import parse_requirements

setup(name='uBooNECRTSlowMon',
      version='1.0',
      description='MicroBooNE CRT Slow Controls Monitoring Script',
      author='Kevin Wierman',
      author_email='kwierman@fnal.gov',
      url='https://github.com/kwierman/uBooNECRTSlowMon',
      packages=find_packages(exclude=[]),
     )