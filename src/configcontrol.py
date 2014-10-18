#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker
"""

import os
import sys
import stat

import yaml

from common.errors import ApplicationError
from utils import fileutils

class ConfigControl():
    """
    Ditz and ditz-gui configuration file provider
    """
    def __init__(self):
        """
        Initialize
        """
        self.ditz_config_file = ".ditz-config"
        self.path_to_config = None

        self.find_ditz_config()

    def find_ditz_config(self, path="."):
        """
        Find ditz configuration file from path toward the root

        Raises:
        - ApplicationError
        """
        try:
            path = fileutils.find_file_along_path(self.ditz_config_file, path)
        except Exception, e:
            raise ApplicationError("Can't find ditz root directory")
        self.path_to_config = path
        return path

    def read_config_file(self):
        """
        Read settings from ditz config file
        """
        pass

    def get_unreleased_releases(self):
        """
        Read names of unreleased releases from Ditz project.yaml file.
        Config file must be read first, or the settings set by other means,
        so we can know where the file can be found.

        Returns:
        - list of release names
        """
        reader = DitzReader("{}/{}".format(self.path_to_config, self.ditz_config_file))
        return reader.read_release_names()


class DitzReader():
    """
    A class to read Ditz project.yaml file
    """
    def __init__(self, config_file):
        self.config_file = config_file
        self.project_file = None

        #TODO: read the project dir from config
        self.project_file = os.path.dirname(config_file) + "/ditz/project.yaml"

    def ditz_project(self, loader, node):
        #--- !ditz.rubyforge.org,2008-03-06/project
        return loader.construct_yaml_map(node)

    def ditz_component(self, loader, node):
        #--- !ditz.rubyforge.org,2008-03-06/component
        return ""

    def ditz_release_name_only(self, loader, node):
        #--- !ditz.rubyforge.org,2008-03-06/release
        # this version returns just the name of the release
        # or None if the release has been released already
        mapping = loader.construct_mapping(node)
        release_status = mapping["status"]
        release_name = mapping["name"]
        if release_status != ":unreleased":
            return None
        return release_name

    def ditz_config(self, loader, node):
        print str(loader.construct_mapping(node))

    def read_ditz_config(self):
        """
        Read configuration settings from Ditz configuration yaml files
        """
        yaml.add_constructor(u"!ditz.rubyforge.org,2008-03-06/config", self.ditz_config)

        stream = open(self.config_file, 'r')
        data = yaml.load(stream)

        print data #TODO

    def read_release_names(self):
        """
        Read names of yet unreleased releases from project.yaml file
        """
        if self.project_file == None:
            raise ApplicationError("Project file location not known")

        #TODO: dont load these again every time(?)
        yaml.add_constructor(u"!ditz.rubyforge.org,2008-03-06/project", self.ditz_project)
        yaml.add_constructor(u"!ditz.rubyforge.org,2008-03-06/component", self.ditz_component)
        yaml.add_constructor(u"!ditz.rubyforge.org,2008-03-06/release", self.ditz_release_name_only)

        stream = open(self.project_file, 'r')
        data = yaml.load(stream)

        releases = data["releases"]
        releases = filter(lambda a: a != None, releases)
        return releases


