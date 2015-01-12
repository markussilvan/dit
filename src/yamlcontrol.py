#! /usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import datetime
import glob
import os
import hashlib

from common.items import DitzIssue
from common.errors import ApplicationError

def str_representer(self, data):
    tag = None
    if '\n' in data:
        style = '|'
    else: style = None
    try:
        data = unicode(data, 'ascii')
        tag = u'tag:yaml.org,2002:str'
    except UnicodeDecodeError:
        try:
            data = unicode(data, 'utf-8')
            tag = u'tag:yaml.org,2002:str'
        except UnicodeDecodeError:
            data = data.encode('base64')
            tag = u'tag:yaml.org,2002:binary'
            style = '|'
    return self.represent_scalar(tag, data, style=style)

yaml.add_representer(str, str_representer)

def datetime_representer(dumper, data):
    value = unicode(data.isoformat(' ') + ' Z')
    return dumper.represent_scalar(u'tag:yaml.org,2002:timestamp', value)

yaml.add_representer(datetime.datetime, datetime_representer)


class IssueYamlControl():
    """
    Class to read and write issue YAML files
    """
    def __init__(self):
        """
        Initialize new IssueYamlControl
        """
        self.issue_dir = "../ditz"          #TODO: hardcoded paths and names (do like ConfigControl does)
        self.issue_prefix = "issue-"        # check where else these are hardcoded and fix with a common solution

    def read_issue_yaml(self, identifier):
        """
        Read an existing issue from a YAML file.

        Parameters:
        - identifier: SHA hash identifier of the issue

        Returns:
        - issue data as a IssueYamlObject
        """
        issue_file = "{}/{}{}.yaml".format(self.issue_dir, self.issue_prefix, identifier)
        with open(issue_file, 'r') as stream:
            issue_data = yaml.load(stream)
            return issue_data
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
        os.remove(issue_file)

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
            sha.update(datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S-{}".format(i)))
            identifier = sha.hexdigest()
            if identifier not in identifiers:
                return identifier

        raise ApplicationError("Unable to generate unique issue identifier")

class IssueYamlObject(yaml.YAMLObject):
    """
    Issue to and from YAML conversion (meta)class
    """

    yaml_tag = u'!ditz.rubyforge.org,2008-03-06/issue'

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
        self.type = issue_type                  #TODO: different variable name possible?
        self.component = component
        self.release = release
        self.reporter = reporter
        self.status = status
        self.disposition = disposition
        self.creation_time = creation_time
        self.references = references
        self.id = identifier                    #TODO: different variable name possible?
        self.log_events = log_events
        super(IssueYamlObject, self).__init__()

    @classmethod
    def fromDitzIssue(cls, issue):
        """
        Initialize a new IssueYamlObject from an existing DitzIssue object

        Parameters:
        - issue: a DitzItem issue
        """
        issue_type = issue.issue_type
        if issue_type and issue_type[0] != ":":
            issue_type = ':' + issue_type

        status = issue.status
        status = status.replace(' ', '_')
        if status and status[0] != ':':
            status = ':' + status

        if issue.disposition == None:
            disposition = ''
        else:
            disposition = issue.disposition

        return cls(issue.title, issue.description, issue_type, issue.component, issue.release,
                issue.creator, status, disposition, issue.created, issue.references,
                issue.identifier, issue.log)

    def toDitzIssue(self):
        """
        Create a new DitzIssue containing the information in this class

        Returns:
        - new DitzIssue
        """
        issue_type = self.type
        if issue_type and issue_type[0] == ':':
            issue_type = issue_type[1:]

        status = self.status
        if status and status[0] == ':':
            status = status[1:]
        status = status.replace('_', ' ')

        # identifier used also as name (name is generated and can't be known yet)
        return DitzIssue(self.title, self.id, issue_type, self.component, status, None,
                self.desc, self.reporter, self.creation_time, self.release,
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


