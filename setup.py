#!/usr/bin/env python
from setuptools import find_packages
from distutils.core import setup
from pip.req import parse_requirements
import pip

install_reqs = parse_requirements("requirements.txt", session=pip.download.PipSession())
reqs = [str(ir.req) for ir in install_reqs]

setup(name='uBooNECRTSlowMon',
      version='1.0',
      description='MicroBooNE CRT Slow Controls Monitoring Script',
      author='Kevin Wierman',
      author_email='kwierman@fnal.gov',
      url='https://github.com/kwierman/uBooNECRTSlowMon',
      requires = reqs,
      packages=find_packages(exclude=[]),
     )