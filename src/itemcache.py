#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker
"""

from common.items import DitzIssue

class ItemCache():
    """
    This class form a cache of read issues and releases
    to memory for faster and easier access.

    A cache is required so issues can be enumerated and named.
    """
    def __init__(self):
        """
        Initialize ItemCache.
        """
        self.issues = []
        self.releases = []

    def add_issue(self, issue):
        """
        Add new issue to cache.
        If the issue already exists in the cache, it is overwritten.
        Old issue is removed and new issue is appended to the end of the cache.

        Parameters:
        - issue: a new issue to add to cache
        """
        # check if given issue contains required information
        if not isinstance(issue, DitzIssue):
            return False
        if issue.title == None or issue.title == "":
            return False
        if issue.identifier == None or issue.identifier == "":
            return False
        if issue.created == None or issue.created == "":
            return False

        # check if the same issue already exists in cache
        # if it does, remove it, but use the same name for the new issue
        for cached_issue in self.issues:
            if cached_issue.identifier == issue.identifier:
                issue.name = cached_issue.name
                self.issues.remove(cached_issue)
                break

        # add the new issue to cache
        self.issues.append(issue)
        return True

    def get_issue(self, identifier):
        """
        Get a cache issue.

        Parameters:
        - identifier: issue name or identifier hash

        Returns:
        - cached issue
        - None if issue not found with given identifier
        """
        for issue in self.issues:
            if issue.identifier == identifier:
                return issue
            if issue.name == identifier:
                return issue

        return None

    def remove_issue(self, identifier):
        """
        Remove issue from cache.

        Parameters:
        - identifier: issue name or identifier hash

        Returns:
        - True if issue was removed successfully
        - False if issue was not found
        """
        for issue in self.issues:
            if issue.identifier == identifier:
                self.issues.remove(issue)
                return True
        return False

    def sort_issues(self, rename=False):
        """
        Sort the cached issues.
        Issues are sorted by creation date.

        Parameters:
        - rename: rename issues according to new sorted order
        """
        self.issues.sort(key=lambda issue: issue.created)
        if rename:
            self.rename_issues()

    def get_issues_by_release(self, release_title, include_closed=False):
        """
        Get all issues belonging to a particular release.

        Parameters:
        - release: name of the release to find the issues for
        - include_closed: list also closed tasks

        Returns:
        - list of issues for that release
        """
        release_issues = []
        for issue in self.issues:
            if issue.release == release_title:
                if include_closed != False or issue.status != "closed":
                    release_issues.append(issue)

        return release_issues

    def get_issue_status_by_id(self, identifier):
        """
        Get status of an issue loaded in the cached list of issues.

        Parameters:
        - identifier: hash or name identifier of an issue

        Returns:
        - issue status
        - None if requested issue is not found
        """
        for item in self.issues:
            if item.name == identifier:
                return item.status
        return None

    def add_release(self, release):
        """
        Add new release to cache.
        If the release already exists in the cache, it is overwritten.
        Old release is removed and new release is appended to the end of the cache.

        Parameters:
        - release: a new release to add to cache
        """
        if not release:
            return False
        if release.title == None or release.title == "":
            return False

        # check if the same release already exists in cache
        for cached_release in self.releases:
            if cached_release.title == release.title:
                self.releases.remove(cached_release)
                break

        # add the new release to cache
        self.releases.append(release)
        return True

    def get_release(self, release_title):
        """
        Find a release from cache by name. First match is returned.

        Parameters:
        - release_title: name of the release
        """
        for release in self.releases:
            if release.title == release_title:
                return release

    def sort_releases(self):
        """
        Sort cached issues.
        """
        #TODO: sort releases by name / creation / semantic versioning / index (new variable)?
        pass

    def clear(self):
        """
        Clear all issues and releases from cache.
        """
        self.issues[:] = []
        self.releases[:] = []

    def rename_issues(self):
        """
        Regenerate names for cached issues.
        Old names, if any, are overwritten.
        Naming convention is <component>-<index>.
        """
        for i, issue in enumerate(self.issues):
            if issue.component != None and issue.component != "":
                prefix = '{}-'.format(issue.component)
            else:
                prefix = 'issue-'
            issue.name = '{}{}'.format(prefix, i+1)

    def get_issue_name_max_len(self):
        """
        Get length of the longest issue name found in cache

        Returns:
        - length of longest issue name as integer
        """
        max_len = 0
        for issue in self.issues:
            if issue.name and len(issue.name) > max_len:
                max_len = len(issue.name)
        return max_len

