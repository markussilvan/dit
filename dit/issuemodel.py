#! /usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import glob
import os
import hashlib
import random
import yaml

from common.items import DitIssue              # pylint: disable=F0401
from common.errors import ApplicationError      # pylint: disable=F0401


class IssueModel(object):
    """
    Class to read and write issue YAML files
    """
    def __init__(self, issue_dir):
        """
        Initialize new IssueModel
        """
        self.issue_dir = issue_dir
        self.issue_prefix = "issue-"

    def read_issue_yaml(self, identifier):
        """
        Read an existing issue from a YAML file.

        Parameters:
        - identifier: SHA hash identifier of the issue

        Returns:
        - issue data as a IssueYamlObject
        """
        issue_file = "{}/{}{}.yaml".format(self.issue_dir, self.issue_prefix, identifier)
        try:
            with open(issue_file, 'r') as stream:
                issue_data = yaml.load(stream, Loader=yaml.Loader)
                return issue_data
        except Exception:
            raise ApplicationError("Error reading issue yaml file")

    def write_issue_yaml(self, issue):
        """
        Write issue data to a YAML file.

        Parameters:
        - issue: issue data as a IssueYamlObject
        """
        issue_file = "{}/{}{}.yaml".format(self.issue_dir, self.issue_prefix, issue.id)
        try:
            with open(issue_file, 'w') as stream:
                yaml_data = yaml.dump(issue, default_flow_style=False, explicit_start=True)
                stream.write(yaml_data)
        except Exception:
            raise ApplicationError("Error writing issue yaml file")

    def remove_issue_yaml(self, identifier):
        """
        Remove issue .yaml file

        Parameters:
        - identifier: issue hash identifier
        """
        issue_file = "{}/{}{}.yaml".format(self.issue_dir, self.issue_prefix, identifier)
        try:
            os.remove(issue_file)
        except Exception:
            raise ApplicationError("Error removing issue yaml file")

    def list_issue_identifiers(self):
        """
        Return a list of all known issue identifiers.

        Returns:
        - a list of valid issue identifiers
        """
        issue_file_format = '/issue-*.yaml'
        issue_files = glob.glob(self.issue_dir + issue_file_format)
        identifiers = []

        # loop all issue files
        for i, f in enumerate(issue_files):
            # first remove everything else except regular files
            if not os.path.isfile(f):
                issue_files.pop(i)
                continue
            identifiers.append(f[-45:-5])

        return identifiers

    def generate_new_identifier(self):
        """
        Generates a new unique identifier hash for an issue.

        Returns:
        - new issue identifier string
        """
        identifiers = self.list_issue_identifiers()
        sha = hashlib.sha1()
        for i in range(10):
            sha.update(datetime.datetime.utcnow().strftime(
                "%Y%m%d%H%M%S-{}-{}".format(i, random.randint(0, 10000))).encode('utf-8'))
            identifier = sha.hexdigest()
            if identifier not in identifiers:
                return identifier

        raise ApplicationError("Unable to generate unique issue identifier")


class IssueYamlObject(yaml.YAMLObject):
    """
    Issue to and from YAML conversion (meta)class
    """

    yaml_tag = u'!dit.random.org,2008-03-06/issue'

    def __init__(self, title, desc, issue_type, component, release, reporter, status, disposition,
            creation_time, references, identifier, log_events):
        """
        Initialize a new IssueYamlObject from given parameters

        Parameters:
        - title: issue title
        - desc: issue description
        - issue_type: type of the issue
        - component: component the issue belongs
        - release: issue is part of given release
        - reporter: person who created the issue
        - status: status of the issue (unstarted, in progress, paused)
        - disposition: (fixed, ...)
        - creation_time: when the issue was created (a datetime in UTC)
        - references: references of this issue
        - identifier: SHA hash identifier of this issue
        - log_events: log of changes and comments to this issue
        """
        self.title = title
        self.desc = desc
        self.type = issue_type
        self.component = component
        self.release = release
        self.reporter = reporter
        self.status = status
        self.disposition = disposition
        self.creation_time = creation_time
        self.references = references
        self.id = identifier
        self.log_events = log_events
        super(IssueYamlObject, self).__init__()

    @classmethod
    def from_dit_issue(cls, issue):
        """
        Initialize a new IssueYamlObject from an existing DitIssue object

        Parameters:
        - issue: a DitItem issue
        """
        issue_type = issue.issue_type
        if issue_type and issue_type[0] != ":":
            issue_type = ':' + issue_type

        status = issue.status
        status = status.replace(' ', '_')
        if status and status[0] != ':':
            status = ':' + status

        if issue.disposition is None:
            disposition = ''
        else:
            disposition = issue.disposition

        return cls(issue.title, issue.description, issue_type, issue.component, issue.release,
                issue.creator, status, disposition, issue.created, issue.references,
                issue.identifier, issue.log)

    def to_dit_issue(self):
        """
        Create a new DitIssue containing the information in this class

        Returns:
        - new DitIssue
        """
        issue_type = self.type
        if issue_type and issue_type[0] == ':':
            issue_type = issue_type[1:]

        status = self.status
        if status and status[0] == ':':
            status = status[1:]
        status = status.replace('_', ' ')

        disposition = self.disposition
        if disposition and disposition[0] == ':':
            disposition = disposition[1:]

        release = self.release
        if release == '':
            release = None

        # identifier used also as name (name is generated and can't be known yet)
        return DitIssue(self.title, self.id, issue_type, self.component, status, disposition,
                self.desc, self.reporter, self.creation_time, release,
                self.references, self.id, self.log_events)

    def __repr__(self):
        return "{} (title={}, desc={}, type={}, component={}, release={}, reporter={}, status={},\
                disposition={}, creation_time={}, references={}, id={}, log_events={})".format(
                self.__class__.__name__,
                self.title,
                self.desc,
                self.type,
                self.component,
                self.release,
                self.reporter,
                self.status,
                self.disposition,
                self.creation_time,
                self.references,
                self.id,
                self.log_events)
