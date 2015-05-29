#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
A unit test for itemcache.py
"""

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

import string
import random
from datetime import datetime

import itemcache
from common.items import DitzIssue

class NullWriter:
    """A class to use as output, when no screen output is wanted."""
    def __init__(self):
        pass
    def write(self, string):
        pass

class testItemCache(unittest.TestCase):
    """Unit test for itemcache.

    ItemCache is used to cache read issues and releases
    to memory for faster and easier access.

    A cache is required so issues can be enumerated and named.
    """
    def setUp(self):
        self.out = NullWriter()
        self.cache = itemcache.ItemCache()

    def createRandomIssue(self):
        """Create a valid issue to use for testing."""
        title = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(16)])
        identifier = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(40)])
        name = identifier
        issue_type = random.choice([':bugfix', ':feature', ':task'])
        description = "lorem ipsum dolor sit ameth"
        release = "v{}.{}".format(random.randint(0, 2), random.randint(0, 12))
        return DitzIssue(title, name, issue_type, 'unittest', ':unstarted', None,
                description, "A tester <mail@address.com>", datetime.now(), release,
                None, identifier, None)

    def testAddingInvalidIssues(self):
        original_count = len(self.cache.issues)
        self.assertEqual(self.cache.add_issue(None), False)
        self.assertEqual(self.cache.add_issue("foo"), False)
        self.assertEqual(self.cache.add_issue(123), False)

        # adding issues with invalid creation time
        invalid = DitzIssue('foo title', 'bar name', ':bugfix', 'fail', ':unstarted', None,
                'This issue is invalid. For testing purposes.', 'Teppo the Tester')
        invalid.identifier = "abcd123"
        self.assertEqual(self.cache.add_issue(invalid), False)
        invalid.created = ""
        self.assertEqual(self.cache.add_issue(invalid), False)
        invalid.release = "FooBar v1.0"
        invalid.created = None
        self.assertEqual(self.cache.add_issue(invalid), False)

        # invalid identifier
        invalid.title = "lol"
        invalid.created = datetime.now()
        invalid.identifier = None
        self.assertEqual(self.cache.add_issue(invalid), False)
        invalid.identifier = ''
        self.assertEqual(self.cache.add_issue(invalid), False)

        # invalid title
        invalid.identifier = 'abcdfeg1234567'
        invalid.title = ''
        self.assertEqual(self.cache.add_issue(invalid), False)
        invalid.title = None
        self.assertEqual(self.cache.add_issue(invalid), False)

        self.assertEqual(len(self.cache.issues), original_count)

    def testAddingAndGettingIssues(self):
        """Adding issues and access them successfully"""
        new_issue_count = 20
        original_count = len(self.cache.issues)
        for i in xrange(new_issue_count):
            issue = self.createRandomIssue()
            self.assertTrue(self.cache.add_issue(issue))
            self.assertIsNotNone(self.cache.get_issue(issue.identifier))
        new_count = len(self.cache.issues)
        self.assertEqual(new_count, original_count + new_issue_count)

    def testRemovingIssue(self):
        """Removing an issue that exists"""
        original_count = len(self.cache.issues)

        # add issue
        issue = self.createRandomIssue()
        self.assertTrue(self.cache.add_issue(issue))
        self.assertIsNotNone(self.cache.get_issue(issue.identifier))
        self.assertEqual(len(self.cache.issues), original_count + 1)

        # remove issue
        self.cache.remove_issue(issue.identifier)
        self.assertIsNone(self.cache.get_issue(issue.identifier))
        self.assertEqual(len(self.cache.issues), original_count)

    def testRemovingInvalidIssue(self):
        """Removing an issue that doesn't exist"""
        original_count = len(self.cache.issues)
        identifier = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(20)])
        self.assertIsNone(self.cache.get_issue(identifier))
        self.assertFalse(self.cache.remove_issue(identifier))

    # implemented in ItemCache:
        #def sort_issues(self, rename=False):
        #def get_issues_by_release(self, release_title, include_closed=False):
        #def get_issue_status_by_id(self, identifier):
        #def add_release(self, release):
        #def get_release(self, release_title):
        #def sort_releases(self):
        #def clear(self):
        #def rename_issues(self):
        #def get_issue_name_max_len(self):
    #self.assertRaises(AttributeError, self.cache.add_issue, None)


def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(testItemCache))
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
