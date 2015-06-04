#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
A unit test for classes in issuemodel.py
"""

import unittest
import re
from datetime import datetime
import os

import testlib
import issuemodel                               # pylint: disable=F0401
from common.errors import ApplicationError      # pylint: disable=F0401
from common.items import DitzIssue              # pylint: disable=F0401


class IssueYamlObjectTests(unittest.TestCase):
    """Unit tests for IssueYamlObject."""
    def setUp(self):
        self.out = testlib.NullWriter()

    def test_converting_from_ditz_issue(self):
        """Convert IssueYamlObject from an existing DitzIssue object"""
        title = "A test issue"
        description = """"This issue is a generated DitzIssue to be converted
        to a DitzYamlObject. Just a simple testing issue with no other purpose."""
        identifier = "abcd1234"
        issue = issuemodel.DitzIssue(title, 'gui-12', 'task', 'unittest', 'unstarted', None,
                description, "A tester <mail@address.com>", datetime.now(), 'v1.0',
                None, identifier, None)
        data = issuemodel.IssueYamlObject.from_ditz_issue(issue)
        self.assertIsInstance(data, issuemodel.IssueYamlObject)
        self.assertEqual(data.title, title)
        self.assertEqual(data.desc, description)
        self.assertEqual(data.type, ':task')
        self.assertEqual(data.component, 'unittest')
        self.assertEqual(data.release, 'v1.0')
        self.assertEqual(data.reporter, "A tester <mail@address.com>")
        self.assertEqual(data.status, ':unstarted')
        self.assertEqual(data.disposition, '')
        self.assertEqual(data.references, [])
        self.assertEqual(data.id, identifier)
        self.assertIsNone(data.log_events)

    def test_converting_from_invalid_ditz_issue(self):
        """Try to convert an invalid DitzIssue to IssueYamlObject"""
        self.assertRaises(AttributeError, issuemodel.IssueYamlObject.from_ditz_issue, None)
        #TODO: is this a bug? should there be more error handling in issuemodel?

    def test_converting_to_ditz_issue(self):
        """Convert IssueYamlObject to a new DitzIssue object"""
        title = "A test issue"
        description = """"This issue is a generated DitzIssue to be converted
        to a DitzYamlObject. Just a simple testing issue with no other purpose."""
        identifier = "97876123512skajdfh2134jh"
        yaml_issue = issuemodel.IssueYamlObject(title, description,
                ':feature', 'lolwut', '2',
                'some@one.com', ':closed', ':fixed',
                datetime.now(), None, identifier, None)
        self.assertIsInstance(yaml_issue, issuemodel.IssueYamlObject)
        try:
            issue = yaml_issue.to_ditz_issue()
        except Exception:
            self.fail("Unexpected exception")
        self.assertIsInstance(issue, DitzIssue)
        self.assertEqual(issue.title, title)
        self.assertEqual(issue.description, description)
        self.assertEqual(issue.issue_type, 'feature')
        self.assertEqual(issue.component, 'lolwut')
        self.assertEqual(issue.release, '2')
        self.assertEqual(issue.creator, 'some@one.com')
        self.assertEqual(issue.status, 'closed')
        self.assertEqual(issue.disposition, 'fixed')
        self.assertEqual(issue.identifier, identifier)
        self.assertIsInstance(issue.references, list)
        self.assertIsNone(issue.log)

    def test_converting_invalid_yaml_object_to_ditz_issue(self):
        """Try to convert an invalid IssueYamlObject into a DitzIssue"""
        self.skipTest("There is no error checking in DitzItem, should there be?")
        #TODO: should there be more error checking in DitzItem, so invalid items wont be created?
        #title = "An another test issue"
        description = "A broken issue for testing."
        identifier = "97823489asd7f98asdf6asdf987asdf987asd"
        yaml_issue = issuemodel.IssueYamlObject(None, description,
                'INVALID_TYPE', 'lolwut', '2',
                'some@one.com', ':closed', ':fixed',
                datetime.now(), None, identifier, None)
        self.assertIsInstance(yaml_issue, issuemodel.IssueYamlObject)
        #self.assertRaises(Exception, yaml_issue.to_ditz_issue())
        # or
        #issue = yaml_issue.to_ditz_issue()
        #self.assertEqual(issue, None)


class IssueModelTests(unittest.TestCase):
    """Unit tests for IssueModel."""
    def setUp(self):
        self.out = testlib.NullWriter()
        self.model = issuemodel.IssueModel()
        self.model.issue_dir = "data/bugs"

    def test_listening_issue_identifiers(self):
        """List identifiers of issues found"""
        try:
            identifiers = self.model.list_issue_identifiers()
        except Exception:
            self.fail("Exception raised")
        self.assertIsInstance(identifiers, list)
        self.assertTrue(len(identifiers) > 1)
        self.assertIsNotNone(re.match(r'[a-f0-9]{40}', identifiers[0]))
        self.assertNotEqual(identifiers[0], identifiers[1])

    def test_generating_identifiers(self):
        """Generate issue identifiers"""
        identifiers = []
        for _ in xrange(10):
            try:
                identifier = self.model.generate_new_identifier()
            except ApplicationError:
                self.fail("Application error raised, unable to create unique identifier")
            except Exception:
                self.fail("Exception raised")
            self.assertIsNotNone(identifier)
            self.assertNotIn(identifier, identifiers)
            identifiers.append(identifier)

    def test_reading_issue_yaml(self):
        """Parse a known good issue .yaml file"""
        identifier = 'e50d0e38b19c1ff0e9b696ffe919435d26477975'
        try:
            data = self.model.read_issue_yaml(identifier)
        except ApplicationError:
            self.fail("Reading issue yaml file failed")
        except Exception:
            self.fail("Unknown exception raised")
        self.assertIsInstance(data, issuemodel.IssueYamlObject)

    def test_reading_nonexistent_yaml(self):
        """Try to read a .yaml file which doesn't exist"""
        identifier = self.model.generate_new_identifier()
        self.assertRaises(ApplicationError, self.model.read_issue_yaml, identifier)

    def test_writing_issue_yaml(self):
        """Try writing a new issue to a .yaml file"""
        title = "A generated test issue"
        description = "This is a boring description of an issue used for testing."
        identifier = "abc123"
        created = datetime.strptime("2015-06-03 16:06:19.950025", "%Y-%m-%d %H:%M:%S.%f")
        issue = issuemodel.DitzIssue(title, 'gui-12', 'task', 'unittest', 'unstarted', None,
                description, "A tester <mail@address.com>", created, 'v1.0',
                None, identifier, None)
        data = issuemodel.IssueYamlObject.from_ditz_issue(issue)
        self.assertIsInstance(data, issuemodel.IssueYamlObject)
        try:
            self.model.write_issue_yaml(data)
        except ApplicationError:
            self.fail("Writing issue yaml file failed")
        except Exception:
            self.fail("Unknown exception raised")

    def test_removing_issue_yaml(self):
        """Try to remove a issue .yaml file"""
        identifier = "TEMPORARY_TO_BE_REMOVED"
        issue_file = "{}/{}{}.yaml".format(self.model.issue_dir,
                self.model.issue_prefix, identifier)

        # create a file first
        self.assertFalse(os.path.exists(issue_file))
        with open(issue_file, 'a'):
            os.utime(issue_file, None)
        self.assertTrue(os.path.exists(issue_file))

        # then remove it
        try:
            self.model.remove_issue_yaml(identifier)
        except ApplicationError:
            self.fail("Removing issue file failed")
        except Exception:
            self.fail("Unknown exception raised")

        self.assertFalse(os.path.exists(issue_file))

    def test_removing_unexistent_issue_yaml(self):
        """Try to remove a issue .yaml file that does not exist"""
        identifier = self.model.generate_new_identifier()
        self.assertRaises(ApplicationError, self.model.remove_issue_yaml, identifier)


def suite():
    """Test suite"""
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(IssueYamlObjectTests))
    testsuite.addTest(unittest.makeSuite(IssueModelTests))
    return testsuite

if __name__ == '__main__':
    testlib.parse_arguments_and_run_tests(suite)

