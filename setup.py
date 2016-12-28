#!/usr/bin/env python
from setuptools import find_packages
from distutils.core import setup


def parse_requirements(requirements):
    f = open(requirements,'r')
    req=[]
    for l in f.readlines():
        if not l.startswith('#'):
            req.append(l.strip('\n'))
    return (i for i in req)


requirements = parse_requirements('requirements.txt')


setup(name='uBooNECRTSlowMon',
      version='1.0',
      description='MicroBooNE CRT Slow Controls Monitoring Script',
      author='Kevin Wierman',
      author_email='kwierman@fnal.gov',
      url='https://github.com/kwierman/uBooNECRTSlowMon',
      requires = requirements,
      packages=find_packages(exclude=[]),
     )