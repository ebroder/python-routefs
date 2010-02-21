#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name="RouteFS",
    version="1.1.0",
    description="RouteFS: A FUSE API wrapper based on URL routing",
    author="Evan Broder",
    author_email="broder@mit.edu",
    url="http://github.com/ebroder/python-routefs/wikis",
    license="MPL, GPL",
    packages=find_packages(),
    install_requires=['fuse_python>=0.2a', 'Routes>=1.7'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)',
        'License :: DFSG approved',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python'
        ]
)
