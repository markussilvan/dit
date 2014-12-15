#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker
"""

from abc import ABCMeta, abstractmethod
import datetime

import common.utils.time

class DitzItem(object):
    """
    A Ditz item abstract baseclass.

    An item can be an issue or an release.
    The object can contain all data of that
    particular item or just the type and a title.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, title):
        """
        Initialize new DitzItem.

        All kinds of items must have a title.

        Parameters:
        - title: item title
        """
        self.title = title

    @abstractmethod
    def __str__(self):
        pass


class DitzRelease(DitzItem):
    """
    A Ditz item containing the information of a release.
    """
    def __init__(self, title, name=None):
        """
        Initialize new DitzRelease.
        """
        super(DitzRelease, self).__init__(title)
        self.name = name

    def __str__(self):
        """
        Serialize to string. Mimic output of Ditz command line.
        """
        item_str = "Release {}".format(self.title)
        return item_str


class DitzIssue(DitzItem):
    """
    A Ditz item containing information of an issue.

    The item can contain all data of that particular issue or
    just the type and a title.
    A status is also commonly set for issues.
    """
    def __init__(self, title, name=None, issue_type=None, component=None,
            status=None, disposition="", description=None, creator=None, created=None,
            release=None, references=[], identifier=None, log=None):
        """
        Initialize new DitzItem.
        At least type and title must be set for releases.
        For issues, also status should be set.
        """
        super(DitzIssue, self).__init__(title)
        self.name = name
        self.issue_type = issue_type
        self.component = component
        self.status = status
        self.disposition = disposition
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
        if self.created:
            created_ago = utils.time.human_time_diff(self.created.isoformat(' '))
        else:
            created_ago = "?"

        item_str = "Issue {}\n{}\n".format(self.name, len(self.name) * '-') + \
            "Title: {}\n".format(self.title) + \
            "Description:\n{}\n".format(self.description) + \
            "Type: {}\n".format(self.issue_type) + \
            "Status: {}\n".format(self.status) + \
            "Creator: {}\n".format(self.creator) + \
            "Created: {}\n".format(created_ago) + \
            "Release: {}\n".format(self.release)

        if self.component != None and self.component != "":
            item_str += "Component: {}\n".format(self.component)

        item_str += "References:\n"
        if self.references:
            for i, reference in enumerate(self.references):
                item_str += "    {}. {}\n".format(i+1, reference)

        item_str += "Identifier: {}\n".format(self.identifier)

        # event log entries
        if self.log:
            for entry in self.log:
                # timestamp, creator, action, comment
                timestamp = utils.time.human_time_diff(entry[0].isoformat(' '))
                creator = entry[1]
                action = entry[2]
                comment = entry[3]
                #entry_str = "- {} ({}, {})\n".format(action, creator, timestamp)
                entry_str = "---------------------------------\n"
                entry_str += "- {}, {}\n".format(action, timestamp)
                entry_str += "  {}\n".format(creator)
                if comment != None and comment != "":
                    entry_str += "  {}\n".format(comment)
                item_str += entry_str

        return item_str

    def add_log_entry(self, timestamp=None, action='comment', creator='Unknown', comment=None):
        """
        Add a new log entry to an issue

        Parameters:
        - timestamp: (optional) creation timestamp of the log entry, now by default
        - action: (optional) title describing what was done, just a comment by default
        - creator: who made the change
        - comment: (optional) a comment to the log, empty by default
        """
        log_entry = [] # format: [ timestamp, creator, action, comment ]
        if timestamp == None:
            timestamp = datetime.datetime.utcnow()
        if creator == None:
            creator = '{} <{}>'.format(self.config.settings.name, self.config.settings.email)
        if comment == None:
            comment = ''
        log_entry.append(timestamp)
        log_entry.append(creator)
        log_entry.append(action)
        log_entry.append(comment)
        if not self.log:
            self.log = []
        self.log.append(log_entry)

