#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import codecs

from setuptools import setup, find_packages

try:
    # Python 3
    from os import dirname
except ImportError:
    # Python 2
    from os.path import dirname

here = os.path.abspath(dirname(__file__))
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()


if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel upload")
    sys.exit()

required = [
    "zmq",
    "numpy",
    "pandas",
    "scikit-learn",
    "python-xlib",
    "Pillow",
    "simplejson",
    "pyinotify"
]

extras_require = {
    'whereami': ['whereami']
}

setup(
    name='brightml',
    version='0.0.0',
    description='Machine Learned Auto brightness',
    long_description=long_description,
    author='Pascal van Kooten',
    author_email='kootenpv@gmail.com',
    url='https://github.com/kootenpv/brightml',
    packages=find_packages(),
    install_requires=required,
    license='MIT',
    entry_points={
        'console_scripts': ['brightml = brightml.__main__:main']
    },
    extras_require=extras_require,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'

    ],
)
