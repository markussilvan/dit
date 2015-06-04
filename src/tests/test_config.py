#! /usr/bin/env python
# A dirty unit test for config.py which contains
# classes to access ditz and ditz-gui settings
#
# Uses all classes in config.py without mocking each class
# out of the equation individually.
# That would require more work than it's worth.

import unittest
import re
import os

import testlib
import config

class ConfigRealTests(unittest.TestCase):
    """
    Unit test for config.

    These tests access real data in ditz-gui repository
    (as the project root is found automatically by the code).
    No data should be modified by these tests.
    """
    def setUp(self):
        self.out = testlib.NullWriter()
        self.config = config.ConfigControl()

        self.config.load_configs()

    def test_verify_loading_configs(self):
        """Verify loading config files"""
        ditzconfig = self.config.get_ditz_configs()
        self.assertTrue(isinstance(ditzconfig, config.DitzConfigYaml))

        appconfig = self.config.get_app_configs()
        self.assertTrue(isinstance(appconfig, config.AppConfigYaml))

    def test_project_root(self):
        """Try reading and verifying project root setting"""
        root = self.config.get_project_root()
        self.assertIsNotNone(root)
        self.assertTrue(isinstance(root, str))
        known_root = os.path.abspath('..')
        self.assertTrue(root, known_root)

    def test_project_name(self):
        """Verify project name"""
        name = self.config.get_project_name()
        self.assertEqual(name, "ditz-gui")

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
        mock_project_root = os.path.abspath('data/')
        self.config.set_project_root(mock_project_root)
        self.config.load_configs()

    def test_project_root(self):
        """Try reading and verifying project root setting"""
        root = self.config.get_project_root()
        self.assertIsNotNone(root)
        self.assertTrue(isinstance(root, str))
        mock_project_root = os.path.abspath('data/')
        self.assertTrue(root, mock_project_root)

    def test_verify_loading_configs(self):
        """Verify loading config files"""
        ditzconfig = self.config.get_ditz_configs()
        self.assertTrue(isinstance(ditzconfig, config.DitzConfigYaml))

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
        self.assertEquals(releases[1].log[0][1], 'Beyonce Bugger <bb@lightningmail.com>')
        self.assertEquals(releases[1].log[0][2], 'created')

    def test_writing_ditz_config(self):
        """
        Write .ditz-config file

        Original data is read already. Change some data,
        read new data to verify, then change it back and
        read it to verify original data has been written back.
        """
        # save original state
        ditzconfig = self.config.ditzconfig
        self.assertIsInstance(ditzconfig, config.DitzConfigModel)
        original_name = ditzconfig.settings.name
        self.assertNotEqual(original_name, 'Boyle Bugger')

        # change creator in ditz configuration
        ditzconfig.settings.name = 'Boyle Bugger'
        self.assertTrue(ditzconfig.write_config_file())
        self.assertTrue(ditzconfig.read_config_file())

        # verify changed creator
        creator = self.config.get_default_creator()
        self.assertEquals(creator, 'Boyle Bugger <bb@lightningmail.com>')

        # change back original values
        ditzconfig.settings.name = original_name
        self.assertTrue(ditzconfig.write_config_file())
        self.assertTrue(ditzconfig.read_config_file())

        # verify original creator
        creator = self.config.get_default_creator()
        self.assertEquals(creator, original_name + ' <bb@lightningmail.com>')


def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(ConfigRealTests))
    testsuite.addTest(unittest.makeSuite(ConfigMockDataTests))
    return testsuite

if __name__ == '__main__':
    testlib.parse_arguments_and_run_tests(suite)


