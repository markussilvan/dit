#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
A unit test for itemcache.py
"""

import unittest
import re
import string                                       # pylint: disable=W0402
import random
from datetime import datetime, timedelta

import testlib
import itemcache                                    # pylint: disable=F0401
from common.items import DitzIssue, DitzRelease     # pylint: disable=F0401

class ItemCacheTests(unittest.TestCase):
    """Unit test for ItemCache.

    ItemCache is used to cache read issues and releases
    to memory for faster and easier access.

    A cache is required so issues can be enumerated and named.
    """
    def setUp(self):
        self.out = testlib.NullWriter()
        self.cache = itemcache.ItemCache()

    def create_random_issue(self, release=None):
        """Create a valid issue to use for testing."""
        title = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(16)])
        identifier = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(40)])
        name = identifier
        issue_type = random.choice(['bugfix', 'feature', 'task'])
        description = "lorem ipsum dolor sit ameth"
        if release is None:
            release = "v{}.{}".format(random.randint(0, 2), random.randint(0, 12))
        return DitzIssue(title, name, issue_type, 'unittest', 'unstarted', None,
                description, "A tester <mail@address.com>", datetime.now(), release,
                None, identifier, None)

    def create_random_release(self):
        """Create a valid release to use for testing."""
        name = ''.join([random.choice(string.printable) for _ in xrange(16)])
        status = random.choice(['unreleased', 'released'])
        return DitzRelease(name, 'Release', status, datetime.now(), None)

    def fill_cache_with_some_data(self, new_issue_count, new_release_count):
        for _ in xrange(new_issue_count):
            issue = self.create_random_issue()
            self.assertTrue(self.cache.add_issue(issue))
            self.assertIsNotNone(self.cache.get_issue(issue.identifier))
        for _ in xrange(new_release_count):
            release = self.create_random_release()
            self.assertTrue(self.cache.add_release(release))
            self.assertIsNotNone(self.cache.get_release(release.title))

    def test_adding_invalid_issues(self):
        original_count = self.cache.issue_count()
        self.assertEqual(self.cache.add_issue(None), False)
        self.assertEqual(self.cache.add_issue("foo"), False)
        self.assertEqual(self.cache.add_issue(123), False)

        # adding issues with invalid creation time
        invalid = DitzIssue('foo title', 'bar name', 'bugfix', 'fail', 'unstarted', None,
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

        self.assertEqual(self.cache.issue_count(), original_count)

    def test_adding_and_getting_issues(self):
        """Adding issues and access them successfully"""
        new_issue_count = 20
        original_count = self.cache.issue_count()
        for _ in xrange(new_issue_count):
            issue = self.create_random_issue()
            self.assertTrue(self.cache.add_issue(issue))
            self.assertIsNotNone(self.cache.get_issue(issue.identifier))
        new_count = self.cache.issue_count()
        self.assertEqual(new_count, original_count + new_issue_count)

    def test_removing_issue(self):
        """Removing an issue that exists"""
        original_count = self.cache.issue_count()

        # add issue
        issue = self.create_random_issue()
        self.assertTrue(self.cache.add_issue(issue))
        self.assertIsNotNone(self.cache.get_issue(issue.identifier))
        self.assertEqual(self.cache.issue_count(), original_count + 1)

        # remove issue
        self.cache.remove_issue(issue.identifier)
        self.assertIsNone(self.cache.get_issue(issue.identifier))
        self.assertEqual(self.cache.issue_count(), original_count)

    def test_removing_invalid_issue(self):
        """Removing an issue that doesn't exist"""
        original_count = self.cache.issue_count()
        identifier = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(20)])
        self.assertIsNone(self.cache.get_issue(identifier))
        self.assertFalse(self.cache.remove_issue(identifier))
        self.assertEquals(self.cache.issue_count(), original_count)

    def test_clearing_cache(self):
        """Clearing the cache with and without existing items)"""
        # test with one issue
        self.cache.clear()
        self.assertEquals(self.cache.issue_count(), 0)
        self.assertEquals(self.cache.release_count(), 0)
        self.assertTrue(self.cache.add_issue(self.create_random_issue()))
        self.assertEquals(self.cache.issue_count(), 1)
        self.assertEquals(self.cache.release_count(), 0)

        # test with one release
        self.cache.clear()
        self.assertEquals(self.cache.issue_count(), 0)
        self.assertEquals(self.cache.release_count(), 0)
        self.assertTrue(self.cache.add_release(self.create_random_release()))
        self.assertEquals(self.cache.issue_count(), 0)
        self.assertEquals(self.cache.release_count(), 1)

        # clearing twice
        self.cache.clear()
        self.cache.clear()
        self.assertEquals(self.cache.issue_count(), 0)
        self.assertEquals(self.cache.release_count(), 0)

    def test_removing_from_empty_cache(self):
        """Try to remove nonexisting issue from an empty cache"""
        self.cache.clear()
        self.assertEquals(self.cache.issue_count(), 0)
        identifier = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(35)])
        self.assertFalse(self.cache.remove_issue(identifier))
        self.assertEquals(self.cache.issue_count(), 0)

    def test_adding_and_getting_releases(self):
        """Add releases and access them successfully"""
        new_releases_count = 10
        original_count = self.cache.release_count()
        for _ in xrange(new_releases_count):
            release = self.create_random_release()
            self.assertTrue(self.cache.add_release(release))
            self.assertIsNotNone(self.cache.get_release(release.title))
        new_count = self.cache.release_count()
        self.assertEqual(new_count, original_count + new_releases_count)

        self.assertTrue(self.cache.add_release(DitzRelease("foo v1.0")))
        self.assertEqual(self.cache.release_count(), new_count + 1)

    def test_adding_invalid_releases(self):
        original_count = self.cache.release_count()
        self.assertFalse(self.cache.add_release(None))
        self.assertFalse(self.cache.add_release("foo"))
        self.assertFalse(self.cache.add_release(123))

        # adding releases with invalid title
        invalid = DitzRelease('')
        self.assertFalse(self.cache.add_release(invalid))
        invalid = DitzRelease(None)
        self.assertFalse(self.cache.add_release(invalid))

        # check that no releases have been added to cache
        self.assertEqual(self.cache.release_count(), original_count)

    def test_removing_release(self):
        """Removing a release that exists"""
        original_issue_count = self.cache.issue_count()
        original_release_count = self.cache.release_count()

        # add release
        release = self.create_random_release()
        self.assertTrue(self.cache.add_release(release))
        self.assertIsNotNone(self.cache.get_release(release.title))
        self.assertEqual(self.cache.issue_count(), original_issue_count)
        self.assertEqual(self.cache.release_count(), original_release_count + 1)

        # remove release
        self.cache.remove_release(release.title)
        self.assertIsNone(self.cache.get_release(release.title))
        self.assertEqual(self.cache.issue_count(), original_issue_count)
        self.assertEqual(self.cache.release_count(), original_release_count)

    def test_removing_invalid_release(self):
        """Trying to remove a release that doesn't exist"""
        original_issue_count = self.cache.issue_count()
        original_release_count = self.cache.release_count()
        random_title = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(12)])
        self.assertIsNone(self.cache.get_release(random_title))
        self.assertFalse(self.cache.remove_release(random_title))
        self.assertEqual(self.cache.issue_count(), original_issue_count)
        self.assertEqual(self.cache.release_count(), original_release_count)

    def test_getting_issue_name_max_length(self):
        """Get length of longest issue name used"""
        new_issue_count = 30
        new_release_count = 10
        self.fill_cache_with_some_data(new_issue_count, new_release_count)

        # add issue with longest name
        issue = self.create_random_issue()
        issue.name = "thelongestnamethisissuehas".join([random.choice(string.printable) for _ in xrange(100)])
        self.assertTrue(self.cache.add_issue(issue))

        # verify it as the longest name
        self.assertEqual(self.cache.get_issue_name_max_len(), len(issue.name))

    def test_renaming_issues(self):
        """Rename issue to use "<component>-<index>" naming"""
        self.cache.clear()
        issue = self.create_random_issue()
        issue.component = "foobar"
        self.cache.add_issue(issue)
        self.cache.rename_issues()
        self.assertEqual('foobar-1', self.cache.issues[0].name)

        new_issue_count = 20
        new_release_count = 5
        self.fill_cache_with_some_data(new_issue_count, new_release_count)
        original_issue_count = self.cache.issue_count()
        original_release_count = self.cache.release_count()
        self.cache.rename_issues()
        self.assertEqual(self.cache.issue_count(), original_issue_count)
        self.assertEqual(self.cache.release_count(), original_release_count)

        self.assertEqual('foobar-1', self.cache.issues[0].name)
        self.assertIsNotNone(re.match(r'^(unittest-\d+)$', self.cache.issues[1].name))

        for i in xrange(10):
            index = random.randint(1, new_issue_count)
            self.assertIsNotNone(re.match(r'^(unittest-\d+)$', self.cache.issues[index].name))

        issue = self.create_random_issue()
        issue.component = None
        self.assertTrue(self.cache.add_issue(issue))
        self.cache.rename_issues()

        self.assertEqual('foobar-1', self.cache.issues[0].name)
        for i in xrange(1, 21):
            self.assertIsNotNone(re.match(r'^(unittest-\d+)$', self.cache.issues[i].name))
        self.assertEqual('issue-22', self.cache.issues[21].name)   #TODO: is this a bug? should it be "issue-1" instead?

    def test_getting_issue_status(self):
        """Get issue status by id"""
        new_issue_count = 10
        new_release_count = 2
        self.fill_cache_with_some_data(new_issue_count, new_release_count)
        issue = self.create_random_issue()
        self.assertTrue(self.cache.add_issue(issue))
        self.assertTrue(self.cache.get_issue(issue.identifier))
        status = self.cache.get_issue_status_by_id(issue.identifier)
        self.assertIsNotNone(status)
        if not status in ['unstarted', 'in progress', 'closed']:
            self.fail("Issue in invalid state")

    def test_getting_issue_status_with_invalid_id(self):
        """Try to get issue status with invalid id"""
        new_issue_count = 10
        new_release_count = 2
        self.fill_cache_with_some_data(new_issue_count, new_release_count)
        identifier = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(8)])
        self.assertFalse(self.cache.get_issue(identifier))
        self.assertIsNone(self.cache.get_issue_status_by_id(identifier))

    def test_getting_issue_status_with_invalid_id_from_empty_cache(self):
        """Try to get issue status with invalid id from empty cache of issues and releases"""
        self.cache.clear()
        identifier = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(8)])
        self.assertIsNone(self.cache.get_issue_status_by_id(identifier))

    def test_get_issues_by_release(self):
        """Get issues belonging to a given release"""
        rel_title = 'test_rel_1'
        new_issue_count = 30
        new_release_count = 4
        self.fill_cache_with_some_data(new_issue_count, new_release_count)

        # add a known release
        release = self.create_random_release()
        release.title = rel_title
        self.cache.add_release(release)

        # add issues that belong to that release
        issues_in_release_count = 10
        for _ in xrange(issues_in_release_count):
            self.cache.add_issue(self.create_random_issue(release=rel_title))

        # get issues in the release
        issues = self.cache.get_issues_by_release(rel_title, True)
        self.assertIsNotNone(issues)
        self.assertEqual(len(issues), issues_in_release_count)
        self.assertEqual(self.cache.issue_count(), new_issue_count + issues_in_release_count)

    def test_try_getting_issues_for_invalid_release(self):
        """
        Try getting issues for a release which doesn't contain issues
        or for a release which doesn't exist in cache.

        Issues are mapped to releases based to release name that is
        set in each issue. Release name in issue should match with
        release title (but current system doesn't require that).

        Release <-> issue integrity is maintained on other parts of
        the software. Item cache is just a cache. (Often updated or
        refreshed from the outside.)
        """
        new_issue_count = 30
        new_release_count = 4
        self.fill_cache_with_some_data(new_issue_count, new_release_count)

        # create a release, but don't add it to cache, get issues
        release = self.create_random_release()
        self.assertIsNone(self.cache.get_release(release.title))
        issues = self.cache.get_issues_by_release(release)
        self.assertIsNotNone(issues)
        self.assertEqual(len(issues), 0)

        # add an empty known release to cache, get issues
        release = self.create_random_release()
        self.assertIsNone(self.cache.get_release(release.title))
        self.assertTrue(self.cache.add_release(release))
        issues = self.cache.get_issues_by_release(release)
        self.assertIsNotNone(issues)
        self.assertEqual(len(issues), 0)

    def test_sorting_issues_no_rename(self):
        """Sorting issues without renaming them."""
        new_issue_count = 30
        new_release_count = 4
        self.fill_cache_with_some_data(new_issue_count, new_release_count)
        original_issues = list(self.cache.issues)               # copy the list
        self.cache.sort_issues()
        self.assertEqual(original_issues, self.cache.issues)    # order should not have changed

        # add an old issue
        issue = self.create_random_issue()
        # 15 years ago from the day of writing this btw
        issue.created = datetime(2000, 6, 2, 0, 0)
        self.assertTrue(self.cache.add_issue(issue))
        self.cache.sort_issues()

        # check that first item in the list has changed (that "old" issue is now first)
        self.assertEqual(self.cache.issues[0], issue)
        self.assertNotEqual(original_issues[0], self.cache.issues[0])
        self.assertEqual(original_issues[0], self.cache.issues[1])

        # add another "new" issue
        issue = self.create_random_issue()
        issue.created = datetime.now() + timedelta(minutes = 10)
        self.assertTrue(self.cache.add_issue(issue))
        self.cache.sort_issues()
        self.assertEqual(self.cache.issues[-1], issue)
        self.assertEqual(original_issues, self.cache.issues[1:-1])

    def test_sorting_issues(self):
        """Sorting issues and renaming them in the process."""
        new_issue_count = 30
        new_release_count = 4
        self.fill_cache_with_some_data(new_issue_count, new_release_count)
        original_issues = list(self.cache.issues)               # copy the list
        self.cache.sort_issues(rename=True)
        self.assertEqual(original_issues, self.cache.issues)    # nothing should have changed

        issue = self.create_random_issue()
        issue.component = "lolz"
        self.assertTrue(self.cache.add_issue(issue))
        another_issue = self.create_random_issue()
        another_issue.component = None
        self.assertTrue(self.cache.add_issue(another_issue))
        self.cache.sort_issues(rename=True)

        # order should not have changed, just new issues added to the end
        # as issues are sorted to creation order
        self.assertEqual(original_issues, self.cache.issues[:-2])
        self.assertEqual(self.cache.issues[-2], issue)
        self.assertEqual(self.cache.issues[-1], another_issue)

        self.assertIsNotNone(re.match(r'^(unittest-\d+)$', self.cache.issues[0].name))
        self.assertIsNotNone(re.match(r'^(unittest-\d+)$', self.cache.issues[1].name))
        self.assertIsNotNone(re.match(r'^(issue-\d+)$', self.cache.issues[-1].name))
        self.assertIsNotNone(re.match(r'^(lolz-\d+)$', self.cache.issues[-2].name))

    #def test_sorting_releases(self):
    #    self.cache.sort_releases()
    #    self.fail("Not implemented")


def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(ItemCacheTests))
    return testsuite

if __name__ == '__main__':
    testlib.parse_arguments_and_run_tests(suite)
