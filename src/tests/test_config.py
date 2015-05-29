#! /usr/bin/env python
# A dirty unit test for config.py which contains
# classes to access ditz and ditz-gui settings
#
# Uses all classes in config.py without mocking each class
# out of the equation individually.
# That would require more work than it's worth.

import unittest
import xmlrunner
import argparse
import re

# allow imports from parent directory
import os, sys, inspect
script_path = os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])
parent_path = os.path.realpath(script_path + "/..")
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

import config

class NullWriter:
    """A class to use as output, when no screen output is wanted."""
    def __init__(self):
        pass
    def write(self, string):
        pass

#TODO: could this be done using separate config files only for testing?
class testConfig(unittest.TestCase):
    """Unit test for config."""
    def setUp(self):
        self.out = NullWriter()
        self.config = config.ConfigControl()

        self.config.load_configs()

    def testVerifyLoadingConfigs(self):
        """Verify loading config files"""
        ditzconfig = self.config.get_ditz_configs()
        self.assertTrue(isinstance(ditzconfig, config.DitzConfigYaml))

        appconfig = self.config.get_app_configs()
        self.assertTrue(isinstance(appconfig, config.AppConfigYaml))

    def testProjectRoot(self):
        """Try reading and verifying project root setting"""
        root = self.config.get_project_root()
        self.assertIsNotNone(root)
        self.assertTrue(isinstance(root, str))
        #print "ROOT: " + root

    def testProjectName(self):
        """Verify project name"""
        name = self.config.get_project_name()
        self.assertEqual(name, "ditz-gui")

    def testListingReleases(self):
        """Check list of releases"""
        releases = self.config.get_releases()
        self.assertTrue(isinstance(releases, list))

    def testIssueStates(self):
        """Check a list of issue states"""
        states = self.config.get_valid_issue_states()
        self.assertIsInstance(states, list)

    def testReleaseStates(self):
        """Check a list of release states"""
        states = self.config.get_valid_release_states()
        self.assertIsInstance(states, list)

    def testDefaultCreator(self):
        """Check default creator"""
        creator = self.config.get_default_creator()
        self.assertIsInstance(creator, str)
        self.assertTrue(len(creator) > 5)
        match = re.search(r'(.+\ <.+>)', creator).groups(0)[0]
        self.assertEquals(match, creator)


def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(testConfig))
    return testsuite

def runTests(use_xml_runner, report_dir):
    if use_xml_runner == True:
        # run tests and generate XML reports from test results
        # default report directory is reports/
        xmlrunner.XMLTestRunner(output=report_dir).run(suite())
    else:
        # run tests and print test output to console
        unittest.TextTestRunner(verbosity=2).run(suite())

if __name__ == '__main__':
    # parse command line arguments and run tests accordingly
    parser = argparse.ArgumentParser(description='Run unit tests.')
    parser.add_argument('--xml', dest='xml', action='store_true', help='type of test run, Text or XML')
    parser.add_argument('out', nargs='?', default="reports",
            help='location for XML test reports')
    args = parser.parse_args()

    runTests(args.xml, args.out)


