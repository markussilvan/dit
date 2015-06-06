#! /usr/bin/env python
#
# A unit test for ArchiveControl.
#
# Tests all functionality in archivecontrol.py.
# Mock test data from data/ subdirectory is used if needed
# and everything there is restored to original state on
# a successful test run.
#

import unittest
import mock
import os
from datetime import datetime                   # pylint: disable=W0611
from shutil import copy2                        # pylint: disable=W0611

import testlib
import archivecontrol                           # pylint: disable=F0401
from ditzcontrol import DitzControl             # pylint: disable=F0401
from config import ConfigControl                # pylint: disable=F0401
from common.errors import ApplicationError      # pylint: disable=F0401
from common.utils import fileutils              # pylint: disable=F0401, W0611
from common.items import DitzIssue              # pylint: disable=F0401, W0611
from common.items import DitzRelease            # pylint: disable=F0401, W0611


class DitzSettingsMock(object):
    """
    A mock of settings structure provided by DitzConfigYaml
    """
    def issue_dir(self):
        return "bugs"
    def name(self):
        return "Erkki el Tester"
    def email(self):
        return "erkkie@yahoo.com"


class ArchiveControlTests(unittest.TestCase):
    """
    Unit test for ArchiveControl.
    """
    def setUp(self):
        self.out = testlib.NullWriter()
        self.archive_dir = os.path.abspath('data/')

    def create_archivecontrol_with_mocks(self):
        """
        Create an instance of ArchiveControl with
        all external interfaces mocked.
        """
        # mock internal interfaces
        title = 'testing issue'
        description = 'foo bar baz bug'
        created = datetime.now()
        identifier = 'asdfasdfasdf123412341234'
        issue = DitzIssue(title, 'gui-12', 'task', 'unittest', 'unstarted', None,
                description, "A tester <mail@address.com>", created, 'v1.0',
                None, identifier, None)
        #release = DitzRelease('unittest-release')
        ditz = mock.Mock(spec=DitzControl)
        ditz.config = mock.Mock(spec=ConfigControl)
        ditz.config.get_ditz_configs.return_value = DitzSettingsMock()
        ditz.config.get_project_root.return_value = 'data/'
        ditz.get_issues_by_release.return_value = [issue]

        # create archive control
        try:
            archiver = archivecontrol.ArchiveControl(ditz)
        except ApplicationError:
            self.fail("Mocked DitzControl not accepted as real DitzControl")
        return archiver

    def test_create_archivecontrol_invalid_ditz(self):
        """Try to create an ArchiveControl instance with invalid DitzControl specified"""
        self.assertRaises(ApplicationError, archivecontrol.ArchiveControl, None)
        self.assertRaises(ApplicationError, archivecontrol.ArchiveControl, 123)
        self.assertRaises(ApplicationError, archivecontrol.ArchiveControl, "123")
        self.assertRaises(ApplicationError, archivecontrol.ArchiveControl, self)
        self.assertRaises(ApplicationError, archivecontrol.ArchiveControl, -1)

    def test_archiving_unexistent_release(self):
        """Try to archive a release that does not exist"""
        archiver = self.create_archivecontrol_with_mocks()
        release_name = 'Unknown release'
        self.assertRaises(ApplicationError, archiver.archive_release, release_name, self.archive_dir)

    @mock.patch('shutil.copy2', return_value = True)
    @mock.patch('common.utils.fileutils.move_files', return_value = True)
    def test_archiving_release(self, mock_move_files, mock_copy2):
        """Simulate archiving a release with all interfaces mocked"""
        archiver = self.create_archivecontrol_with_mocks()
        release_name = 'week 49'
        try:
            archiver.archive_release(release_name, self.archive_dir)
        except ApplicationError:
            self.fail("Unexpected ApplicationError raised")
        except Exception:
            self.fail("Unknown exception raised")

        mock_move_files.assert_called_once_with(mock.ANY, mock.ANY)
        mock_copy2.assert_called_once_with(mock.ANY, self.archive_dir + '/project.yaml')

    # do a real archiving test (separate class?)
    # try archiving an unresolved release. or should that be allowed?
    # try archiving a release containing issues
    # try archiving a release not containing issues
    # try archiving a release that is already archived

def suite():
    """Test suite including all tests in this file"""
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(ArchiveControlTests))
    return testsuite

if __name__ == '__main__':
    testlib.parse_arguments_and_run_tests(suite)


