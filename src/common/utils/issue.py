#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
General utilities for issue handling
"""

class IssueUtils(object):
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
        state_order = {
            "in progress": 0,
            "paused": 1,
            "unstarted": 2,
            "closed": 3
        }
        return state_order.get(issue.status, 3)
