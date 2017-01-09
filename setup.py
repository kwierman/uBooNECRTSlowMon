#!/usr/bin/env python
from setuptools import find_packages
from distutils.core import setup
from pip.req import parse_requirements
import pip
import os

install_reqs = parse_requirements("requirements.txt", session=pip.download.PipSession())
reqs = [str(ir.req) for ir in install_reqs]

scripts=[os.path.join('./scripts',i) for i in os.listdir('./scripts')]

setup(name='uBooNECRTSlowMon',
      version='1.9',
      description='MicroBooNE CRT Slow Controls Monitoring Script',
      author='Kevin Wierman',
      author_email='kwierman@fnal.gov',
      url='https://github.com/kwierman/uBooNECRTSlowMon',
      install_requires = reqs,
      packages=find_packages(exclude=[]),
      scripts=scripts
     )