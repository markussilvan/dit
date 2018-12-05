#! /usr/bin/env python3
#
# A unit test for "unused".
#
# Tests that using usused() doesn't cause any problems.
#

import unittest

import testlib
from common import unused               # pylint: disable=F0401


class CommonUnusedTests(unittest.TestCase):
    """
    Unit test for common unused method.
    """
    def setUp(self):
        self.out = testlib.NullWriter()
        self.foo = 'not used'

    def test_01_unused_local_variable(self):
        """
        Define an unused local variable an pass it to unused().

        This should not cause any pylint warnings from
        variable 'a' not being used.
        """
        a = 1               # this variable won't be used
        unused.unused(a)    # prevents pylint warnings from not using 'a'

    def test_02_unused_class_variable(self):
        """
        Pass unused class variable to unused()

        This would not cause pylint errors even in normal conditions.
        Check that behauvior is not altered in any way.
        """
        unused.unused(self.foo)

    def test_03_try_callind_with_undefined_variable(self):
        """
        Try calling unused() with an undefined variable.
        """
        try:
            unused.unused(lol_wut_not_defined)      # pylint: disable=E0602
        except NameError:
            pass
        else:
            self.fail('Expected exception not raised')


def suite():
    """Test suite including all tests in this file"""
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(CommonUnusedTests))
    return testsuite

if __name__ == '__main__':
    testlib.parse_arguments_and_run_tests(suite)
