#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
General utilities for issue handling
"""

class IssueUtils():
    """
    Class to hold general utils for issue handling
    """
    def __init__(self):
        """
        This class doesn't need to be instantiated.
        """
        pass

    @staticmethod
    def sort_issues_by_status(issues):
        """
        Sort given issues by status. Returns a new sorted list of issues.

        Parameters:
        - issues: list of issues to sort

        Returns:
        - new sorted list
        """
        issues.sort(key=IssueUtils._status_sorting_func)
        return issues

    @staticmethod
    def _status_sorting_func(issue):
        """
        Define sorting order for issue states
        """
        if issue.status == "in progress":
            return 0
        elif issue.status == "paused":
            return 1
        elif issue.status == "unstarted":
            return 2
        else:
            return 3 # closed
