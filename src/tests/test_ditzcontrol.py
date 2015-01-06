#! /usr/bin/env python
# A unit test for ditzcontrol.py which contains
# classes to access Ditz command line tool

import unittest
import xmlrunner
import argparse

# allow imports from parent directory
import os, sys, inspect
script_path = os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])
parent_path = os.path.realpath(script_path + "/..")
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

import ditzcontrol

class NullWriter:
    """A class to use as output, when no screen output is wanted."""
    def __init__(self):
        pass
    def write(self, string):
        pass

class testDitzControl(unittest.TestCase):
    """Unit test for DitzControl."""
    def setUp(self):
        self.out = NullWriter()
        self.dc = ditzcontrol.DitzControl()

    #TODO: this must be run in its own "ditz repo" so effects of the commands can be tested
    #TODO: and the effect can be also verified from the files that ditz creates
    def testClose(self):
        pass

    def testComment(self):
        pass

    def testGetReleases(self):
        releases = self.dc.get_releases(names_only=True)
        self.assertTrue(isinstance(releases, list))
        #print "Releases: " + str(releases)

    #def testGetItems(self):
    #    items = self.dc.get_items()
    #    self.assertTrue(isinstance(items, list))
    #    print "Items: " + str(items)

    #def testGetItem(self):
    #    item = self.dc.get_item("ditz-gui-1")
    #    self.assertTrue(isinstance(item, list))
    #    print "Item: " + str(item)

def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(testDitzControl))
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


