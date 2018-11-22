#! /usr/bin/env python
# A unit test for ditcontrol.py which contains
# classes to access Dit command line tool

import unittest

import testlib
import ditcontrol                              # pylint: disable=F0401
from common.errors import ApplicationError      # pylint: disable=F0401

class DitControlTests(unittest.TestCase):
    """Unit test for DitControl."""
    def setUp(self):
        self.out = testlib.NullWriter()

    def test_construction(self):
        self.assertRaises(ApplicationError, ditcontrol.DitControl, None)

    #TODO: this must be run in its own "dit repo" so effects of the commands can be tested
    #TODO: and the effect can be also verified from the files that dit creates

    #TODO: creating DitControl with mocked ConfigControl inside it is a big job and it relies heavily on it
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
    #    item = self.dc.get_item("dit-gui-1")
    #    self.assertTrue(isinstance(item, list))
    #    print("Item: " + str(item))

def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(DitControlTests))
    return testsuite

if __name__ == '__main__':
    testlib.parse_arguments_and_run_tests(suite)
