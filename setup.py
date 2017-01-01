#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2016-2017 mosquito <sensor.wen@gmail.com>

# Use of this source code is governed by MIT license that can be found
# in the LICENSE file.

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys
import re
import checker


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['-v']
        self.test_suite = True

    def run_tests(self):
        import pytest
        err_code = pytest.main(self.test_args)
        sys.exit(err_code)


with open('requirements.txt', 'r') as f:
    install_deps = re.split("==.*\n", f.read())[0:-1]


setup(
    name=checker.__pkgname__,
    version=checker.__version__,
    license=checker.__license__,
    url=checker.__url__,
    author=checker.__author__,
    author_email=checker.__email__,
    description=checker.__descript__,
    long_description=open('README.md').read(),
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    platforms='any',
    install_requires=install_deps,
    entry_points={
        'console_scripts': [
            'checker = checker:main'
        ],
    },
    test_suite="tests",
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    keywords=['network', 'checker', 'gui'],
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'
    ]
)
