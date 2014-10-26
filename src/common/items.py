#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker
"""

class DitzItem():
    """
    A Ditz item which can be an issue or an release.
    Can contain all data of that particular item or
    just the type and a header.
    A status is also commonly set for issues.
    """
    def __init__(self, item_type, title, name=None, issue_type=None, component=None,
            status=None, disposition=None, description=None, creator=None, created=None,
            release=None, references=None, identifier=None, log=None):
        """
        Initialize new DitzItem.
        At least type and title must be set for releases.
        For issues, also status should be set.
        """
        self.item_type = item_type
        self.name = name

        self.title = title
        self.issue_type = issue_type
        self.component = component
        self.status = status
        self.disposition = ""
        self.description = description
        self.creator = creator
        self.created = created
        self.release = release
        self.references = references
        self.identifier = identifier
        self.log = log

    def __str__(self):
        """
        Serialize to string. Mimic output of Ditz command line.
        """
        return "Issue {}\n{}".format(self.name, len(self.name) * '-') + '\n' + \
            "Title: {}".format(self.title) + '\n' + \
            "Description:\n{}".format(self.description) + '\n' + \
            "Type: {}".format(self.issue_type) + '\n' + \
            "Status: {}".format(self.status) + '\n' + \
            "Creator: {}".format(self.creator) + '\n' + \
            "Created: {}".format(self.created) + '\n' + \
            "Release: {}".format(self.release) + '\n' + \
            "References:\n{}".format(self.references) + \
            "Identifier: {}".format(self.identifier) + '\n' + \
            "Event log:\n{}".format(self.log)
