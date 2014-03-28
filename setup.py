#!/usr/bin/env python
import os
from setuptools import setup, find_packages

setup(name='itemxml',

    # Package structure
    #
    # find_packages searches through a set of directories 
    # looking for packages
    packages = find_packages('src', exclude = ['ez_setup',
        '*.tests', '*.tests.*', 'tests.*', 'tests']),
    # package_dir directive maps package names to directories.
    # package_name:package_directory
    package_dir = {'': 'src'},

    # Not all packages are capable of running in compressed form, 
    # because they may expect to be able to access either source 
    # code or data files as normal operating system files.
    zip_safe = True,

    # Entry points
    #
    # install the executable
    entry_points = { },

    # Dependencies
    #
    # Dependency expressions have a package name on the left-hand 
    # side, a version on the right-hand side, and a comparison 
    # operator between them, e.g. == exact version, >= this version
    # or higher
    requires=['loxun(>=1.3)','intermine(>=1.02.00)'],

    # Tests
    #
    # Tests must be wrapped in a unittest test suite by either a
    # function, a TestCase class or method, or a module or package
    # containing TestCase classes. If the named suite is a package,
    # any submodules and subpackages are recursively added to the
    # overall test suite.
    test_suite = 'itemxml.tests.suite',
    # Download dependencies in the current directory
    tests_require = 'docutils >= 0.6',

    # Meta information
    #
    version='0.1.0',
    description='Items XML production facilities',
    author='Alex Kalderimis',
    author_email='alex@intermine.org',
    url='http://github.com/intermine/itemxml.py'
)

