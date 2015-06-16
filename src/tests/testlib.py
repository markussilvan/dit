#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
A common utilities library for all unit tests.
"""

import unittest
import xmlrunner
import argparse

# allow imports from parent directory
import os, sys, inspect
script_path = os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])
parent_path = os.path.realpath(script_path + "/..")
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

class NullWriter(object):
    """A class to use as output, when no screen output is wanted."""
    def __init__(self):
        pass
    def write(self, string):
        pass

def run_tests(use_xml_runner, report_dir, suite):
    if use_xml_runner == True:
        # run tests and generate XML reports from test results
        # default report directory is reports/
        xmlrunner.XMLTestRunner(output=report_dir).run(suite())
    else:
        # run tests and print test output to console
        unittest.TextTestRunner(verbosity=2).run(suite())

def parse_arguments_and_run_tests(suite):
    # parse command line arguments and run tests accordingly
    parser = argparse.ArgumentParser(description='Run unit tests.')
    parser.add_argument('--xml', dest='xml', action='store_true', help='type of test run, Text or XML')
    parser.add_argument('out', nargs='?', default="reports",
            help='location for XML test reports')
    args = parser.parse_args()

    run_tests(args.xml, args.out, suite)
