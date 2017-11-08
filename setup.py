#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import codecs


from setuptools import setup, find_packages

a = "this is a very long string fjjjjjjor example ifnd padf asdfasdf adsf asdfas dfjjjjjjjjj aadsfasmmmmmmmmm "


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
    "scipy",
    "numpy",
    "pandas",
    "scikit-learn",
    "python-xlib",
    "Pillow",
    "simplejson",
    "pyinotify",
    "watchdog"
]

extras_require = {
    'whereami': ['whereami']
}

# poor man's version parser
with open("brightml/__init__.py") as f:
    for line in f:
        version = line.strip().split()[-1].strip('"')
        break

setup(
    name='brightml',
    version=version,
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
