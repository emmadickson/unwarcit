#!/usr/bin/env python

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

__version__ = '0.0.0'


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)

    def run_tests(self):
        import pytest
        import sys
        import os
        errcode = pytest.main(['--doctest-modules', './unwarcit', '--cov', 'unwarcit', '-v', 'test/'])
        sys.exit(errcode)

setup(
    name='unwarcit',
    version=__version__,
    author='Emma Dickson',
    author_email='emma.jk.dickson@gmail.com',
    license='Apache 2.0',
    packages=find_packages(),
    url='https://github.com/emmadickson/unwarcit',
    description='Unzip and Access Files in Web Archives (WARC) and WACZ Files',
     entry_points="""
        [console_scripts]
        unwarcit = unwarcit.unwarcit:main
        """
)
