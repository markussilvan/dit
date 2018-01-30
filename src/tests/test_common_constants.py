#! /usr/bin/env python
#
# A unit test for common constants in the project.
#
# Tests using constants defined in common/constants.py.
# Checks that values can't be changed.
#

import unittest

import testlib
from common import constants            # pylint: disable=F0401


class CommonConstantsTests(unittest.TestCase):
    """
    Unit test for common errors.
    """
    def setUp(self):
        self.out = testlib.NullWriter()

    def testhelper_add_some_constants(self):
        """
        Helper function for the test below
        """
        constants.lol = constants.Constants(a=1, b=2)
        constants.just_a_test = constants.Constants(it='works')

    def test_01_accessing_constants(self):
        """
        Access some predefined constants
        """
        self.assertEqual(constants.release_states.UNRELEASED, 'unreleased')
        self.assertEqual(constants.release_states.RELEASED, 'released')
        self.assertEqual(constants.releases.UNASSIGNED, 'Unassigned')

    def test_02_trying_to_alter_data(self):
        """
        Trying to change values of constants

        Should result in errors.
        """
        try:
            constants.release_states.UNRELEASED = 'foobar'
        except ValueError:
            pass
        else:
            self.fail('no expected ValueError raised')

    def test_03_new_constant(self):
        """
        Trying to add a new constant

        Should result in errors.
        """
        try:
            constants.release_states.foobar = 'LOL'
        except ValueError:
            pass
        else:
            self.fail('no expected ValueError raised')

    def test_04_new_constant_objects(self):
        """
        Adding new Constant object, which can contain new constants.
        """
        constants.new_things = constants.Constants(foo=1, bar='baz')
        self.assertEqual(constants.new_things.foo, 1)
        self.assertEqual(constants.new_things.bar, 'baz')
        self.assertEqual(constants.releases.UNASSIGNED, 'Unassigned')

        self.testhelper_add_some_constants()
        self.assertEqual(constants.lol.a, 1)
        self.assertEqual(constants.lol.b, 2)
        self.assertEqual(constants.just_a_test.it, 'works')

    def test_05_accessing_constants_as_keys(self):
        """
        Accessing existing constants using "dictionary syntax"

        This is not allowed (or implemented).
        """
        try:
            _ = constants.releases['UNASSIGNED']
        except TypeError:
            pass
        else:
            self.fail('Expected TypeError not raised')


def suite():
    """Test suite including all tests in this file"""
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(CommonConstantsTests))
    return testsuite

if __name__ == '__main__':
    testlib.parse_arguments_and_run_tests(suite)


