#! /usr/bin/env python3
#
# A unit test for ArchiveControl.
#
# Tests all functionality in archivecontrol.py.
# Mock test data from data/ subdirectory is used if needed
# and everything there is restored to original state on
# a successful test run.
#

import unittest
import os
from shutil import rmtree
from shutil import copy2                        # pylint: disable=W0611
from datetime import datetime                   # pylint: disable=W0611

import mock

import testlib
import archivecontrol                           # pylint: disable=F0401
from ditcontrol import DitControl             # pylint: disable=F0401
from config import ConfigControl                # pylint: disable=F0401
from common.errors import ApplicationError      # pylint: disable=F0401
from common.utils import fileutils              # pylint: disable=F0401, W0611
from common.items import DitIssue              # pylint: disable=F0401, W0611
from common.items import DitRelease            # pylint: disable=F0401, W0611


class DitSettingsMock(object):
    """
    A mock of settings structure provided by DitConfigYaml
    """
    def __init__(self):
        self.issue_dir = "bugs"
        self.name = "Erkki el Tester"
        self.email = "erkkie@yahoo.com"


class ArchiveControlTests(unittest.TestCase):
    """
    Unit tests for ArchiveControl that don't access real data on disk.
    """
    def setUp(self):
        self.out = testlib.NullWriter()
        self.archive_dir = 'data/foo'

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
        issue = DitIssue(title, 'gui-12', 'task', 'unittest', 'unstarted', None,
                description, "A tester <mail@address.com>", created, 'v1.0',
                None, identifier, None)
        dit = mock.Mock(spec=DitControl)
        dit.config = mock.Mock(spec=ConfigControl)
        dit.config.get_dit_configs.return_value = DitSettingsMock()
        dit.config.get_project_root.return_value = os.path.abspath('data')
        dit.get_issues_by_release.return_value = [issue]

        # create archive control
        try:
            archiver = archivecontrol.ArchiveControl(dit)
        except ApplicationError:
            self.fail("Mocked DitControl not accepted as real DitControl")
        return archiver

    def test_create_archivecontrol_invalid_dit(self):
        """
        Try to create an ArchiveControl instance with invalid DitControl specified
        """
        self.assertRaises(ApplicationError, archivecontrol.ArchiveControl, None)
        self.assertRaises(ApplicationError, archivecontrol.ArchiveControl, 123)
        self.assertRaises(ApplicationError, archivecontrol.ArchiveControl, "123")
        self.assertRaises(ApplicationError, archivecontrol.ArchiveControl, self)
        self.assertRaises(ApplicationError, archivecontrol.ArchiveControl, -1)

    @mock.patch('shutil.copy2', return_value=True)
    @mock.patch('common.utils.fileutils.move_files', return_value=True)
    def test_archiving_release(self, mock_move_files, mock_copy2):
        """
        Simulate archiving a release with all interfaces mocked
        """
        archiver = self.create_archivecontrol_with_mocks()
        release_name = 'week 49'
        try:
            archiver.archive_release(release_name, self.archive_dir)
        except ApplicationError:
            self.fail("Unexpected ApplicationError raised")
        except Exception:
            self.fail("Unknown exception raised")

        mock_move_files.assert_called_once_with(mock.ANY, mock.ANY)
        mock_copy2.assert_called_once_with(mock.ANY,
                os.path.abspath(self.archive_dir + '/project.yaml'))


class ArchiveControlDataAccessTests(unittest.TestCase):
    """Archiving tests that access data on disk"""

    def setUp(self):
        self.out = testlib.NullWriter()
        self.archive_dir = os.path.abspath('data/archive')
        self.issue_dir = os.path.abspath('data/bugs')
        self.archive_project_file = self.archive_dir + '/project.yaml'

    def tearDown(self):
        # remove archive files (trailing slash is required to get the directory removed)
        try:
            rmtree(self.archive_dir + '/')
        except OSError:
            # not every test creates this directory
            pass

    def create_archivecontrol(self, mock_issues=None):
        """
        Create an instance of ArchiveControl with
        some external interfaces mocked.

        Components that provice data access to archive files
        is left intact.
        """
        # mock internal interfaces
        dit = mock.Mock(spec=DitControl)
        dit.config = mock.Mock(spec=ConfigControl)
        dit.config.get_dit_configs.return_value = DitSettingsMock()
        dit.config.get_project_root.return_value = os.path.abspath('data')

        if mock_issues is None:
            title = 'just a testing issue'
            description = 'foo bar baz bug foo foo poo poo.'
            created = datetime.now()
            identifier = 'some_issue_id'
            issue = DitIssue(title, 'gui-12', 'task', 'unittest', 'unstarted', None,
                    description, "A tester <mail@address.com>", created, 'v1.0',
                    None, identifier, None)
            dit.get_issues_by_release.return_value = [issue]
        else:
            dit.get_issues_by_release.return_value = mock_issues

        # create archive control
        try:
            archiver = archivecontrol.ArchiveControl(dit)
        except ApplicationError:
            self.fail("Mocked DitControl not accepted as real DitControl")
        return archiver

    def test_archiving_unexistent_release(self):
        """
        Try to archive a release that does not exist
        """
        archiver = self.create_archivecontrol()
        release_name = 'Unknown release'
        self.assertRaises(ApplicationError, archiver.archive_release, release_name, self.archive_dir)
        self.assertTrue(os.path.isdir(self.archive_dir))    # archive_release() causes empty
                                                            # archive dir to be created

    def test_real_archiving_with_nonexistent_issue_in_release(self):
        """
        Try to archive a release with contains an issue which
        does not exist on file system.
        """
        archiver = self.create_archivecontrol()
        release_name = 'week 49'
        self.assertRaises(ApplicationError, archiver.archive_release,
                release_name, self.archive_dir)

        self.assertTrue(os.path.isdir(self.archive_dir))

    def test_real_archiving(self):
        """
        Archive a release using actual file system.
        Moves issue files to archive and creates a copy of the project file.
        """
        # set "valid" issue data to archivecontrol (points to a known test issue)
        title = 'do these even matter?'
        description = \
                'No. Content of these fields does not matter.' \
                'Matching an issue to a file is based on its identifier only.'
        created = datetime.now()
        identifier = '1ff0e9be50d779750e3ffe9198b6435d219c6964'
        issue = DitIssue(title, 'gui-12', 'task', 'unittest', 'unstarted', None,
                description, "A tester <mail@address.com>", created, 'v1.0',
                None, identifier, None)
        issues = [issue]

        try:
            # create fake issue file to archive
            real_issue_file = '{}/issue-e50d0e38b19c1ff0e9b696ffe919435d26477975.yaml'.format(self.issue_dir)
            test_issue_file = '{}/issue-{}.yaml'.format(self.issue_dir, identifier)
            copy2(real_issue_file, test_issue_file)
        except Exception:
            self.fail("Creating a test issue to archive failed")

        try:
            archiver = self.create_archivecontrol(issues)
            release_name = 'lolwut'
        except Exception:
            self.fail("Error creating archivecontrol")

        try:
            archiver.archive_release(release_name, self.archive_dir)
        except ApplicationError:
            self.fail("Unexpected ApplicationError raised")
        except Exception:
            self.fail("Unknown exception raised")

        # verify that archive files were created
        self.assertTrue(os.path.isdir(self.archive_dir))
        self.assertTrue(os.path.isfile(self.archive_project_file))
        self.assertEquals(len(os.listdir(self.archive_dir)), 2)

    # try archiving an unresolved release. or should that be allowed?
    # try archiving a release containing only closed issues (should be allowed)
    # try archiving a release containing open issues (should be allowed)
    # try archiving a release not containing issues (should be allowed)
    # try archiving a release that is already archived


def suite():
    """Test suite including all tests in this file"""
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(ArchiveControlTests))
    testsuite.addTest(unittest.makeSuite(ArchiveControlDataAccessTests))
    return testsuite

if __name__ == '__main__':
    testlib.parse_arguments_and_run_tests(suite)
