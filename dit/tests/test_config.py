#! /usr/bin/env python3
#
# A dirty unit test for config.py which contains
# classes to access dit and dit-gui settings
#
# Uses all classes in config.py without mocking each class
# out of the equation individually.
# That would require more work than it's worth.

import unittest
import re
import os
from datetime import datetime

import testlib
import config                                   # pylint: disable=F0401
from common.errors import ApplicationError      # pylint: disable=F0401
from common.items import DitRelease             # pylint: disable=F0401

class ConfigRealTests(unittest.TestCase):
    """
    Unit test for config.

    These tests access real data in dit-gui repository
    (as the project root is found automatically by the code).
    No data should be modified by these tests.
    """
    def setUp(self):
        self.out = testlib.NullWriter()
        self.config = config.ConfigControl()

        self.config.load_configs()

    def test_verify_loading_configs(self):
        """Verify loading config files"""
        ditconfig = self.config.get_dit_configs()
        self.assertTrue(isinstance(ditconfig, config.DitConfigYaml))

        appconfig = self.config.get_app_configs()
        self.assertTrue(isinstance(appconfig, config.AppConfigYaml))

    def test_project_root(self):
        """Try reading and verifying project root setting"""
        root = self.config.get_project_root()
        self.assertIsNotNone(root)
        self.assertTrue(isinstance(root, str))
        known_root = os.path.abspath('data/bugs')
        self.assertTrue(root, known_root)

    def test_project_name(self):
        """Verify project name"""
        name = self.config.get_project_name()
        self.assertEqual(name, "testing_project")

    def test_listing_releases(self):
        """Check list of releases"""
        releases = self.config.get_releases()
        self.assertTrue(isinstance(releases, list))

    def test_issue_states(self):
        """Check a list of issue states"""
        states = self.config.get_valid_issue_states()
        self.assertIsInstance(states, list)

    def test_release_states(self):
        """Check a list of release states"""
        states = self.config.get_valid_release_states()
        self.assertIsInstance(states, list)

    def test_default_creator(self):
        """Check default creator"""
        creator = self.config.get_default_creator()
        self.assertIsInstance(creator, str)
        self.assertTrue(len(creator) > 5)
        match = re.search(r'(.+\ <.+>)', creator).groups(0)[0]
        self.assertEquals(match, creator)


class ConfigMockDataTests(unittest.TestCase):
    """
    Unit test for config.

    These tests use an altered project root.
    This way data is known and can be modified.
    """
    def setUp(self):
        self.out = testlib.NullWriter()
        self.config = config.ConfigControl()
        mock_project_root = os.path.abspath('data/bugs')
        self.config.set_project_root(mock_project_root)
        self.config.load_configs()

    def test_project_root(self):
        """Try reading and verifying project root setting"""
        root = self.config.get_project_root()
        self.assertIsNotNone(root)
        self.assertTrue(isinstance(root, str))
        mock_project_root = os.path.abspath('data/bugs')
        self.assertTrue(root, mock_project_root)

    def test_verify_loading_configs(self):
        """Verify loading config files"""
        ditconfig = self.config.get_dit_configs()
        self.assertTrue(isinstance(ditconfig, config.DitConfigYaml))

        appconfig = self.config.get_app_configs()
        self.assertTrue(isinstance(appconfig, config.AppConfigYaml))

    def test_project_name(self):
        """Verify mock project name"""
        name = self.config.get_project_name()
        self.assertEqual(name, "testing_project")

    def test_default_creator(self):
        """Check default creator"""
        creator = self.config.get_default_creator()
        self.assertEquals(creator, 'Beyonce Bugger <bb@lightningmail.com>')

    def test_valid_issue_states(self):
        """List valid issue states"""
        states = self.config.get_valid_issue_states()
        self.assertEquals(states, ["unstarted", "in progress", "paused"])

    def test_valid_release_states(self):
        """List valid release states"""
        states = self.config.get_valid_release_states()
        self.assertEquals(states, ["unreleased", "released"])

    def test_get_releases(self):
        """Get release information"""
        releases = self.config.get_releases()
        self.assertEquals(releases[0].name, "Release")
        self.assertEquals(releases[0].title, "week 49")
        self.assertEquals(releases[0].status, "unreleased")
        self.assertEquals(releases[0].release_time, None)
        self.assertEquals(releases[1].name, "Release")
        self.assertEquals(releases[1].title, "lolwut")
        self.assertEquals(releases[1].status, "unreleased")
        self.assertEquals(releases[1].release_time, None)
        self.assertEquals(releases[1].log[0][1],
                'Beyonce Bugger <bb@lightningmail.com>')
        self.assertEquals(releases[1].log[0][2], 'created')

    def test_writing_dit_config(self):
        """
        Write .dit-config file

        Original data is read already. Change some data,
        read new data to verify, then change it back and
        read it to verify original data has been written back.
        """
        # save original state
        ditconfig = self.config.ditconfig
        self.assertIsInstance(ditconfig, config.DitConfigModel)
        original_name = ditconfig.settings.name
        self.assertNotEqual(original_name, 'Boyle Bugger')

        # change creator in dit configuration
        ditconfig.settings.name = 'Boyle Bugger'
        self.assertTrue(ditconfig.write_config_file())
        self.assertTrue(ditconfig.read_config_file())

        # verify changed creator
        creator = self.config.get_default_creator()
        self.assertEquals(creator, 'Boyle Bugger <bb@lightningmail.com>')

        # change back original values
        ditconfig.settings.name = original_name
        self.assertTrue(ditconfig.write_config_file())
        self.assertTrue(ditconfig.read_config_file())

        # verify original creator
        creator = self.config.get_default_creator()
        self.assertEquals(creator, original_name + ' <bb@lightningmail.com>')

    def test_reading_nonexistent_appconfig(self):
        """
        Set project root to an invalid location and try to read
        application config file

        See that error is returned and default settings are loaded.
        """
        appconfig = self.config.appconfig
        self.assertIsInstance(appconfig, config.AppConfigModel)
        appconfig.project_root = '/foobar/lolwut/no_one_is_home/'
        self.assertFalse(appconfig.read_config_file())
        self.assertEqual(appconfig.settings.issue_types,
                ['bugfix', 'feature', 'task', 'enhancement'])
        self.assertEqual(appconfig.settings.default_issue_type, 'task')

    def test_writing_appconfig(self):
        """Write application configuration file"""
        appconfig = self.config.appconfig
        self.assertIsInstance(appconfig, config.AppConfigModel)
        self.assertTrue(appconfig.write_config_file())

    def test_get_valid_issue_states(self):
        """Get valid issue states from AppConfigModel"""
        states = self.config.appconfig.get_valid_issue_states()
        self.assertEqual(states, ["unstarted", "in progress", "paused"])

    def test_get_valid_release_states(self):
        """Get valid release states from AppConfigModel"""
        states = self.config.appconfig.get_valid_release_states()
        self.assertEqual(states, ["unreleased", "released"])


class MockProjectConfigTests(unittest.TestCase):
    """ProjectConfigModel tests using mock data"""

    def setUp(self):
        self.out = testlib.NullWriter()
        known_root = os.path.abspath('data/bugs/project.yaml')
        self.pconfig = config.DitProjectModel(known_root)

    def testReadingProjectFile(self):
        """Read known project file"""
        self.assertTrue(self.pconfig.read_config_file())
        self.assertEqual(self.pconfig.project_data.name, "testing_project")
        self.assertEqual(self.pconfig.project_data.version, "0.5")
        self.assertEqual(self.pconfig.project_data.components[0].name, "testing_project")
        self.assertEqual(self.pconfig.project_data.releases[0].name, "week 49")

    def testWritingProjectFile(self):
        """
        Write changes to the project file

        First write changes to the project file, then verify those changes,
        and change the original data back. Verify it - just in case.
        """
        self.assertTrue(self.pconfig.read_config_file())
        original_project_name = self.pconfig.project_data.name
        new_project_name = "foobar project (+1)"
        self.assertNotEqual(original_project_name, new_project_name)
        self.pconfig.project_data.name = new_project_name
        self.assertTrue(self.pconfig.write_config_file())
        self.assertTrue(self.pconfig.read_config_file())
        self.assertEqual(self.pconfig.project_data.name, new_project_name)
        self.pconfig.project_data.name = original_project_name
        self.assertTrue(self.pconfig.write_config_file())
        self.assertTrue(self.pconfig.read_config_file())
        self.assertEqual(self.pconfig.project_data.name, original_project_name)

    def testReadingInvalidProjectFile(self):
        """Try reading project file from an invalid path"""
        self.pconfig.project_file = None
        self.assertFalse(self.pconfig.read_config_file())

    def testWritingInvalidProjectFile(self):
        """Try writing project file to an invalid path"""
        self.pconfig.project_file = None
        self.assertFalse(self.pconfig.write_config_file())

    def test_get_releases(self):
        """Get release information from project file"""
        self.assertTrue(self.pconfig.read_config_file())
        releases = self.pconfig.get_releases()
        self.assertEquals(releases[0].name, "Release")
        self.assertEquals(releases[0].title, "week 49")
        self.assertEquals(releases[0].status, "unreleased")
        self.assertEquals(releases[0].release_time, None)
        self.assertEquals(releases[1].name, "Release")
        self.assertEquals(releases[1].title, "lolwut")
        self.assertEquals(releases[1].status, "unreleased")
        self.assertEquals(releases[1].release_time, None)
        self.assertEquals(releases[1].log[0][1],
                'Beyonce Bugger <bb@lightningmail.com>')
        self.assertEquals(releases[1].log[0][2], 'created')

    def test_get_releases_names_only(self):
        """Get release names only from the project file"""
        self.assertTrue(self.pconfig.read_config_file())
        releases = self.pconfig.get_releases(names_only=True)
        self.assertIsInstance(releases, list)
        self.assertEquals(releases[0], "week 49")
        self.assertEquals(releases[1], "lolwut")

    def test_get_releases_by_state(self):
        """Get releases by state from the project file"""
        self.assertTrue(self.pconfig.read_config_file())
        releases = self.pconfig.get_releases(status='unreleased', names_only=True)
        self.assertIsInstance(releases, list)
        self.assertEquals(releases[0], "week 49")
        self.assertEquals(releases[1], "lolwut")

    def test_get_releases_by_unknown_state(self):
        """Get releases by unknown state from the project file"""
        self.assertTrue(self.pconfig.read_config_file())
        releases = self.pconfig.get_releases(status='foobar', names_only=True)
        self.assertIsInstance(releases, list)
        self.assertEqual(len(releases), 0)

    def test_get_releases_by_invalid_state(self):
        """
        Try to get release names from project file with an
        invalid state parameter"""
        self.assertTrue(self.pconfig.read_config_file())
        self.assertRaises(Exception, self.pconfig.get_releases, 123, True)

    def testAddRemoveReleases(self):
        """
        Add new release and remove it from project file

        First add a new release to a project file and verify it's written correctly.
        Then remove the release and verify it's removed correctly.
        """
        self.assertTrue(self.pconfig.read_config_file())

        # add release and save config
        title = 'TestApp v0.1-beta_prerel'
        release = DitRelease(title, 'LOL', 'released', datetime.now(), None)
        self.pconfig.set_release(release)
        self.assertTrue(self.pconfig.write_config_file())

        # re-read data and verify
        self.assertTrue(self.pconfig.read_config_file())
        releases = self.pconfig.get_releases(status='released', names_only=True)
        self.assertIsInstance(releases, list)
        self.assertEquals(len(releases), 1)
        self.assertEquals(releases[0], title)

        # remove release
        self.assertTrue(self.pconfig.remove_release(title))
        self.assertTrue(self.pconfig.write_config_file())

        # verify everything is back to normal
        self.assertTrue(self.pconfig.read_config_file())
        releases = self.pconfig.get_releases(status='released', names_only=True)
        self.assertIsInstance(releases, list)
        self.assertEquals(len(releases), 0)

        releases = self.pconfig.get_releases(names_only=True)
        self.assertIsInstance(releases, list)
        self.assertEquals(len(releases), 2)
        self.assertEquals(releases[0], "week 49")
        self.assertEquals(releases[1], "lolwut")

    def testRemovingUnexistentOrInvalidRelease(self):
        """Try to remove a release which doesn't exist or use invalid parameters"""
        self.assertTrue(self.pconfig.read_config_file())

        # try removing some nonexistent releases or use invalid parameters
        self.assertFalse(self.pconfig.remove_release('winter is coming'))
        self.assertFalse(self.pconfig.remove_release('123'))
        self.assertFalse(self.pconfig.remove_release(123))
        self.assertFalse(self.pconfig.remove_release(self))
        self.assertFalse(self.pconfig.remove_release(None))

        # check every remains normal
        releases = self.pconfig.get_releases(names_only=True)
        self.assertIsInstance(releases, list)
        self.assertEquals(len(releases), 2)
        self.assertEquals(releases[0], "week 49")
        self.assertEquals(releases[1], "lolwut")

    def testRenameRelease(self):
        """
        Rename an existing release in the project file

        First load releases, change information of a relase, save it to project file.
        Verify changes have been saved correctly and change the information back.
        Verify again.
        """
        self.assertTrue(self.pconfig.read_config_file())

        # rename release and verify it changed
        new_title = 'SuperSoftware_Q1'
        release = self.pconfig.get_releases()[0]
        original_title = release.title
        release.title = new_title
        self.pconfig.set_release(release, old_name=original_title)
        self.assertTrue(self.pconfig.write_config_file())
        self.assertTrue(self.pconfig.read_config_file())
        release = self.pconfig.get_releases()[0]
        self.assertEqual(release.title, new_title)

        # change it back
        release.title = original_title
        self.pconfig.set_release(release, old_name=new_title)
        self.assertTrue(self.pconfig.write_config_file())
        self.assertTrue(self.pconfig.read_config_file())

        # check every remains normal
        releases = self.pconfig.get_releases(names_only=True)
        self.assertIsInstance(releases, list)
        self.assertEquals(len(releases), 2)
        self.assertEquals(releases[0], "week 49")
        self.assertEquals(releases[1], "lolwut")

    def testSetReleaseWithInvalidParameters(self):
        """
        Try to rename or add a release in the project file with invalid combination
        of parameters or unsupported values.

        Verify that no data is changed.
        """
        self.assertTrue(self.pconfig.read_config_file())
        release = self.pconfig.get_releases()[0]
        release.title = None
        self.assertFalse(self.pconfig.set_release(release))
        release.title = "tuut tuut"
        self.assertFalse(self.pconfig.set_release(None))
        self.assertFalse(self.pconfig.set_release(123))
        self.assertFalse(self.pconfig.set_release("123"))
        self.assertFalse(self.pconfig.set_release(release, old_name=123))
        self.assertFalse(self.pconfig.set_release(release, old_name=release))
        self.assertFalse(self.pconfig.set_release(release, old_name='h000t'))
        releases = self.pconfig.get_releases()
        self.assertEquals(len(releases), 2)
        self.assertEquals(releases[0].title, "week 49")
        self.assertEquals(releases[1].title, "lolwut")

    def testMoveRelease(self):
        """Move a release (up in priority)"""
        self.assertTrue(self.pconfig.read_config_file())
        releases = self.pconfig.get_releases(names_only=True)
        release_name = releases[0]
        self.assertTrue(self.pconfig.move_release(release_name, config.MOVE_DOWN))
        releases = self.pconfig.get_releases(names_only=True)
        self.assertEqual(releases[1], release_name)

        # move it back and verify
        self.assertTrue(self.pconfig.move_release(release_name, config.MOVE_UP))
        releases = self.pconfig.get_releases()
        self.assertEquals(len(releases), 2)
        self.assertEquals(releases[0].title, "week 49")
        self.assertEquals(releases[1].title, "lolwut")

    def testMoveNonexistentOrInvalidRelease(self):
        """Try to move a release which doesn't exist"""
        self.assertTrue(self.pconfig.read_config_file())
        self.assertFalse(self.pconfig.move_release('h000t h00t', config.MOVE_UP))
        self.assertFalse(self.pconfig.move_release(None, config.MOVE_DOWN))
        self.assertFalse(self.pconfig.move_release(123, config.MOVE_DOWN))
        self.assertFalse(self.pconfig.move_release(0, config.MOVE_UP))

    def testMoveReleaseNoData(self):
        """Try to move a release if no project data is loaded"""
        self.assertFalse(self.pconfig.move_release('h000t h00t', config.MOVE_DOWN))

    def testReleasing(self):
        """Make a release"""
        self.assertTrue(self.pconfig.read_config_file())
        release = self.pconfig.get_releases()[0]
        self.assertEqual(release.status, 'unreleased')
        self.assertIsNone(release.release_time)

        # make release and verify
        self.pconfig.make_release(release)
        release = self.pconfig.get_releases()[0]
        self.assertEqual(release.status, 'released')
        self.assertIsNotNone(release.release_time)
        self.assertIsInstance(release.release_time, datetime)

    def testReleasingInvalidOrNoData(self):
        """Try to make a release when no data is loaded or given"""
        self.pconfig.make_release(None)
        self.assertTrue(self.pconfig.read_config_file())
        self.pconfig.make_release(None)


def suite():
    """Test suite including all tests in this file"""
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(ConfigRealTests))
    testsuite.addTest(unittest.makeSuite(ConfigMockDataTests))
    testsuite.addTest(unittest.makeSuite(MockProjectConfigTests))
    return testsuite

if __name__ == '__main__':
    testlib.parse_arguments_and_run_tests(suite)
