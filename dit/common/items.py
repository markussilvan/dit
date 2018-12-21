#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dit GUI

A GUI frontend for Dit issue tracker
"""

import os
import datetime
from abc import ABCMeta, abstractmethod

from common import constants
import common.utils.time

class DitItem(object):
    """
    A Dit item abstract baseclass.

    An item can be an issue or an release.
    The object can contain all data of that
    particular item or just the type and a title.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, title):
        """
        Initialize new DitItem.

        All kinds of items must have a title.

        Parameters:
        - title: item title
        """
        self.title = title
        self.log = None

    @abstractmethod
    def __str__(self):
        """
        Representation of the item's content as text.
        """
        pass

    @abstractmethod
    def toHtml(self):
        """
        Representation of the item's content as HTML.
        """
        pass

    def add_log_entry(self, timestamp=None, action='comment', creator='', comment=''):
        """
        Add a new log entry to an item

        Parameters:
        - timestamp: (optional) creation timestamp of the log entry, now by default
        - action: (optional) title describing what was done, just a comment by default
        - creator: who made the change
        - comment: (optional) a comment to the log, empty by default
        """
        log_entry = [] # format: [ timestamp, creator, action, comment ]
        if timestamp is None:
            timestamp = datetime.datetime.utcnow()
        if comment is None:
            comment = ''
        log_entry.append(timestamp)
        log_entry.append(creator)
        log_entry.append(action)
        log_entry.append(comment)
        if not self.log:
            self.log = []
        self.log.append(log_entry)

    def _format_text_to_html(self, text):
        """
        Format long texts, like issue descriptions or comments to HTML
        containing paragraphs.

        Parameters:
        - text: a piece of text to format with HTML tags

        Returns:
        - text with some HTML tags
        """
        text = '<p>' + text
        text = text.replace('\n\n', '</p><p>')
        text = '</p>' + text
        return text

    def _format_log_html(self, template_file):
        """
        Format item's event log to HTML according to a given template file

        Parameters:
        - template: a HTML template file to use

        Returns:
        - log as HTML
        """
        if self.log:
            with open(template_file, 'r') as stream:
                log_template_html = stream.readlines()

            log_html = ''
            for entry in self.log:
                # timestamp, creator, action, comment
                timestamp = common.utils.time.human_time_diff(entry[0].isoformat(' '))
                creator = entry[1]
                action = entry[2]
                if len(entry) > 3:
                    comment = self._format_text_to_html(entry[3])
                else:
                    comment = ''

                entry_html = ''
                for line in log_template_html:
                    line = line.replace('[ACTION]', action, 1)
                    line = line.replace('[TIMESTAMP]', timestamp, 1)
                    line = line.replace('[CREATOR]', creator, 1)
                    line = line.replace('[COMMENT]', comment, 1)
                    entry_html += line

                log_html += entry_html
        else:
            log_html = ''

        return log_html


class DitRelease(DitItem):
    """
    A Dit item containing the information of a release.
    """
    def __init__(self, title, name=None, status=None, release_time=None, log=None):
        """
        Initialize new DitRelease.
        """
        super(DitRelease, self).__init__(title)
        self.name = name
        self.status = status
        self.log = log
        if not self.log:
            self.log = []

        if release_time in [None, ""]:
            self.release_time = None
        else:
            # expected format is 2014-10-11 16:25:53.253218 Z
            try:
                self.release_time = datetime.datetime.strptime(release_time, '%Y-%m-%d %H:%M:%S.%f Z')
            except Exception:
                self.release_time = None

    def __str__(self):
        """
        Serialize to string. Mimic output of Dit command line.
        """
        item_str = "{} {}".format(self.name, self.title)
        return item_str

    def toHtml(self):
        """
        Representation of the release content as HTML.
        """
        my_path = os.path.dirname(os.path.realpath(__file__))
        release_template_file = my_path + '/../../ui/templates/release_template.html'
        release_log_template_file = my_path + '/../../ui/templates/release_log_template.html'

        with open(release_template_file, 'r') as stream:
            template_html = stream.readlines()

        log_html = self._format_log_html(release_log_template_file)

        release_time = self.release_time_as_string()
        if release_time is None:
            release_time = 'N/A'

        # release html output
        html = ''
        for line in template_html:
            line = line.replace('[NAME]', self.name, 1)
            line = line.replace('[TITLE]', self.title, 1)
            if self.status:
                status = self.status
            else:
                status = 'unknown'
            line = line.replace('[STATUS]', status, 1)
            line = line.replace('[RELEASE_TIME]', release_time, 1)
            line = line.replace('[EVENT_LOG]', log_html, 1)
            html += line

        return html

    def can_be_archived(self):
        """
        Check if conditions allow this release to be moved to archive.

        Returns:
        - True if release can be archived
        - False if release shouldn't be archived
        """
        if self.status == 'released':
            return True
        return False

    def release_time_as_string(self):
        """
        Return release time set for this release as string.

        Returns:
        - release time as string
        - None if release time is not set
        """
        if self.release_time:
            return self.release_time.isoformat(' ') + ' Z'
            #return datetime.strftime(self.release_time, '%y-%m-%d %H:%M:%S.%f Z')
        return None


class DitIssue(DitItem):
    """
    A Dit item containing information of an issue.

    The item can contain all data of that particular issue or
    just the type and a title.
    A status is also commonly set for issues.
    """
    def __init__(self, title, name=None, issue_type=None, component=None,
            status=None, disposition="", description=None, creator=None, created=None,
            release=None, references=None, identifier=None, log=None):
        """
        Initialize new DitItem.
        At least type and title must be set for releases.
        For issues, also status should be set.
        """
        super(DitIssue, self).__init__(title)
        self.name = name
        self.issue_type = issue_type
        self.component = component
        self.status = status
        self.disposition = disposition
        self.description = description
        self.creator = creator
        self.created = created
        self.release = release
        if references is not None:
            self.references = references
        else:
            self.references = []
        self.identifier = identifier
        self.log = log

    def __str__(self):
        """
        Serialize to string. Mimic output of Dit command line.
        """
        if self.name is not None:
            name = self.name
        else:
            name = ""

        if self.created:
            created_ago = common.utils.time.human_time_diff(self.created.isoformat(' '))
        else:
            created_ago = "?"

        if self.release is not None:
            release = self.release
        else:
            release = constants.releases.UNASSIGNED

        item_str = "Issue {}\n{}\n".format(name, len(name) * '-') + \
            "Title: {}\n".format(self.title) + \
            "Description:\n{}\n".format(self.description) + \
            "Type: {}\n".format(self.issue_type) + \
            "Status: {}\n".format(self.status) + \
            "Creator: {}\n".format(self.creator) + \
            "Created: {}\n".format(created_ago) + \
            "Release: {}\n".format(release)

        if self.component not in (None, ""):
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
                timestamp = common.utils.time.human_time_diff(entry[0].isoformat(' '))
                creator = entry[1]
                action = entry[2]
                if len(entry) > 3:
                    comment = entry[3]
                else:
                    comment = ''
                #entry_str = "- {} ({}, {})\n".format(action, creator, timestamp)
                entry_str = "---------------------------------\n"
                entry_str += "- {}, {}\n".format(action, timestamp)
                entry_str += "  {}\n".format(creator)
                if comment not in (None, ""):
                    entry_str += "  {}\n".format(comment)
                item_str += entry_str

        return item_str

    def _get_status_color(self):
        """
        Choose a color for status text to print.
        """
        if self.status == 'in progress':
            status_color = '#92F72A'
        elif self.status == 'paused':
            status_color = '#FF0000'
        else:
            status_color = '#0095FF'
        return status_color


    def toHtml(self):
        """
        Representation of the issue content as HTML.
        """
        my_path = os.path.dirname(os.path.realpath(__file__))
        issue_template_file = my_path + '/../../ui/templates/issue_template.html'
        issue_log_template_file = my_path + '/../../ui/templates/issue_log_entry_template.html'

        with open(issue_template_file, 'r') as stream:
            template_html = stream.readlines()

        if self.created:
            created_ago = common.utils.time.human_time_diff(self.created.isoformat(' '))
        else:
            created_ago = "?"

        if self.release is not None:
            release = self.release
        else:
            release = constants.releases.UNASSIGNED

        references_html = '<ol>'
        if self.references:
            for reference in self.references:
                references_html += "<li>{}</li>\n".format(reference)
        references_html += '</ol>'

        log_html = self._format_log_html(issue_log_template_file)

        description = self._format_text_to_html(self.description)

        html = ''
        for line in template_html:
            line = line.replace('[NAME]', self.name, 1)
            line = line.replace('[TITLE]', self.title, 1)
            line = line.replace('[DESCRIPTION]', description, 1)
            line = line.replace('[ISSUE_TYPE]', self.issue_type, 1)
            line = line.replace('[CREATOR]', self.creator, 1)
            line = line.replace('[STATUS]', self.status, 1)
            line = line.replace('[STATUS_COLOR]', self._get_status_color(), 1)
            line = line.replace('[CREATOR]', self.creator, 1)
            line = line.replace('[CREATED]', created_ago, 1)
            line = line.replace('[RELEASE]', release, 1)
            line = line.replace('[COMPONENT]', self.component, 1)
            line = line.replace('[REFERENCES]', references_html, 1)
            line = line.replace('[IDENTIFIER]', self.identifier, 1)
            line = line.replace('[EVENT_LOG]', log_html, 1)
            html += line

        return html
