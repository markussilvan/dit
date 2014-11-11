#! /usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import datetime

from common.items import DitzItem
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
        #issue_file = "{}/{}{}.yaml".format(self.issue_dir, self.issue_prefix, identifier)
        issue_file = "{}/{}{}.yaml".format(self.issue_dir, self.issue_prefix, "TESTI")
        try:
            with open(issue_file, 'w') as stream:
                yaml_data = yaml.dump(issue, default_flow_style=False, explicit_start=True)
                stream.write(yaml_data)
        except Exception:
            raise ApplicationError("Error writing issue yaml file")


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
        self.type = issue_type                  #TODO: eri nimi?
        self.component = component
        self.release = release
        self.reporter = reporter
        self.status = status
        self.disposition = disposition
        self.creation_time = creation_time
        self.references = references            #TODO: osaako tää tehdä listan ihan näin?
        self.id = identifier                    #TODO: eri nimi?
        self.log_events = log_events
        super(IssueYamlObject, self).__init__()

    @classmethod
    def fromDitzItem(cls, item):
        """
        Initialize a new IssueYamlObject from an existing DitzItem object

        Parameters:
        - item: a DitzItem issue
        """
        return cls(item.title, item.description, item.item_type, item.component, item.release,
                item.creator, item.status, item.disposition, item.created, item.references,
                item.identifier, item.log)

    def toDitzItem(self):
        """
        Create a new DitzItem containing the information in this class
        """
        return DitzItem('issue', self.title, self.id, self.type, None, self.status, None,
                self.desc, self.reporter, self.creation_time, self.release,
                self.references, self.id, self.log_events)
        #TODO: identifier used as name as there is no mechanism to generate names yet

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


