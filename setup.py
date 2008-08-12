#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name="RouteFS",
    version="0.0.1",
    description="RouteFS: A FUSE API wrapper based on URL routing",
    author="Evan Broder",
    author_email="broder@mit.edu",
    url="http://ebroder.net/code/RouteFS",
    license="MIT",
    packages=find_packages(),
    install_requires=['fuse_python>=0.2a', 'Routes>=1.7']
)
