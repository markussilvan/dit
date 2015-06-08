#! /usr/bin/env python
#
# A unit test for new exceptions in the project.
#
# Tests all functionality in common/errors.py.
#

import unittest

import testlib
from common.errors import ApplicationError, DitzError      # pylint: disable=F0401


class CommonErrorsTests(unittest.TestCase):
    """
    Unit test for common errors.
    """
    def setUp(self):
        self.out = testlib.NullWriter()
        self.ditz_error_test_message = "foo bar baz !!! 00+++"
        self.application_error_test_message = "this is an error message"

    def lol_func(self, lol):
        """A function used for raising different exceptions in tests."""
        if lol == 1:
            raise ApplicationError(self.application_error_test_message)
        elif lol == 2:
            raise DitzError(self.ditz_error_test_message)

    def test_01_raising_application_error(self):
        """
        Raise an ApplicationError intentionally
        """
        self.assertRaises(ApplicationError, self.lol_func, 1)

    def test_02_raising_ditz_error(self):
        """
        Raise an DitzError intentionally
        """
        self.assertRaises(DitzError, self.lol_func, 2)

    def test_03_raise_application_error_and_check(self):
        """
        Raise an application error and check its content
        """
        try:
            self.lol_func(1)
        except ApplicationError as e:
            self.assertEquals(e.error_message, self.application_error_test_message)
        except Exception:
            self.fail("Unknown exception raised")
        else:
            self.fail("No exception raised")

    def test_04_raise_ditz_error_and_check(self):
        """
        Raise an ditz error and check its content
        """
        try:
            self.lol_func(2)
        except DitzError as e:
            self.assertEquals(e.error_message, self.ditz_error_test_message)
        except Exception:
            self.fail("Unknown exception raised")
        else:
            self.fail("No exception raised")


def suite():
    """Test suite including all tests in this file"""
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(CommonErrorsTests))
    return testsuite

if __name__ == '__main__':
    testlib.parse_arguments_and_run_tests(suite)


