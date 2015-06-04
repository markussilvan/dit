#! /usr/bin/env python
# A unit test for ditzcontrol.py which contains
# classes to access Ditz command line tool

import unittest

import testlib
import ditzcontrol                              # pylint: disable=F0401
from common.errors import ApplicationError      # pylint: disable=F0401

class NullWriter:
    """A class to use as output, when no screen output is wanted."""
    def __init__(self):
        pass
    def write(self, string):
        pass

class DitzControlTests(unittest.TestCase):
    """Unit test for DitzControl."""
    def setUp(self):
        self.out = testlib.NullWriter()

    def test_construction(self):
        self.assertRaises(ApplicationError, ditzcontrol.DitzControl, None)

    #TODO: this must be run in its own "ditz repo" so effects of the commands can be tested
    #TODO: and the effect can be also verified from the files that ditz creates

    #TODO: creating DitzControl with mocked ConfigControl inside it is a big job and it relies heavily on it
    #      thus testing these separately is hard

    #def test_get_releases(self):
    #    releases = self.dc.get_releases(names_only=True)
    #    self.assertTrue(isinstance(releases, list))
    #    #print("Releases: " + str(releases))

    #def test_get_items(self):
    #    items = self.dc.get_items()
    #    self.assertTrue(isinstance(items, list))
    #    print("Items: " + str(items))

    #def test_get_item(self):
    #    item = self.dc.get_item("ditz-gui-1")
    #    self.assertTrue(isinstance(item, list))
    #    print("Item: " + str(item))

def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(DitzControlTests))
    return testsuite

if __name__ == '__main__':
    testlib.parse_arguments_and_run_tests(suite)

