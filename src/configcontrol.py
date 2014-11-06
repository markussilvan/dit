#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker
"""

import yaml

from common.errors import ApplicationError
from common.utils import unused
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

        # Ditz settings from config file
        self.settings = None

        self.find_ditz_config()

    def find_ditz_config(self, path="."):
        """
        Find ditz configuration file from path toward the root

        Raises:
        - ApplicationError
        """
        try:
            path = fileutils.find_file_along_path(self.ditz_config_file, path)
        except Exception:
            raise ApplicationError("Can't find ditz root directory")
        self.path_to_config = path
        return path

    def read_config_file(self):
        """
        Read settings from ditz config file
        Cache the settings in self.settings.

        Returns:
        - a DitzConfig object containing settings
        """
        reader = DitzReader("{}/{}".format(self.path_to_config, self.ditz_config_file))
        self.settings = reader.read_ditz_config()
        return self.settings

    def write_config_file(self):
        """
        Write settings from memory to ditz config file.
        """
        reader = DitzReader("{}/{}".format(self.path_to_config, self.ditz_config_file))
        reader.write_ditz_config(self.settings)

    def get_unreleased_releases(self):
        """
        Read names of unreleased releases from Ditz project.yaml file.
        Config file must be read first, or the settings set by other means,
        so we can know where the file can be found.

        Returns:
        - list of release names
        """
        if self.settings == None:
            return
        if self.settings.issue_dir == None:
            return
        reader = DitzReader("{}/{}".format(self.path_to_config, self.ditz_config_file),
                self.path_to_config + "/" + self.settings.issue_dir + "/project.yaml")
        return reader.read_release_names()


class DitzSettings(yaml.YAMLObject):

    yaml_tag = u'!ditz.rubyforge.org,2008-03-06/config'

    def __init__(self, name, email, issue_dir):
        self.name = name
        self.email = email
        self.issue_dir = issue_dir

    def __repr__(self):
        return "%s (name=%r, email=%r, issue_dir=%r)" % (self.__class__.__name__, self.name, self.email, self.issue_dir)

    #def __getitem__(self,):
    #    return sel
    #def __setitem__(self, key, item):
    #    self.data[key] = item

class DitzReader():
    """
    A class to read Ditz project.yaml file
    """
    def __init__(self, config_file, project_file=None):
        self.config_file = config_file
        self.project_file = project_file

        yaml.add_constructor(u"!ditz.rubyforge.org,2008-03-06/project", self.ditz_project)
        yaml.add_constructor(u"!ditz.rubyforge.org,2008-03-06/component", self.ditz_component)
        yaml.add_constructor(u"!ditz.rubyforge.org,2008-03-06/release", self.ditz_release_name_only)

    def ditz_project(self, loader, node):
        #--- !ditz.rubyforge.org,2008-03-06/project
        return loader.construct_yaml_map(node)

    def ditz_component(self, loader, node):
        #--- !ditz.rubyforge.org,2008-03-06/component
        unused(loader)
        unused(node)
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

    #def ditz_config(self, loader, node):
    #    return loader.construct_mapping(node)

    def read_ditz_config(self):
        """
        Read configuration settings from Ditz configuration yaml file
        """
        #yaml.add_constructor(u"!ditz.rubyforge.org,2008-03-06/config", self.ditz_config)

        with open(self.config_file, 'r') as stream:
            data = yaml.load(stream)
            return data
        raise ApplicationError("Error reading ditz settings file")

    def write_ditz_config(self, settings):
        """
        Write configuration settings to Ditz configuration yaml file.
        Settings currently cached in memory are written to the file.

        Parameters:
        - settings: DitzConfig object containing Ditz settings to write
        """
        try:
            with open(self.config_file, 'w') as stream:
                yaml_data = yaml.dump(settings, default_flow_style=False)
                stream.write(yaml_data)
        except Exception:
            raise ApplicationError("Error writing ditz settings file")

    def read_release_names(self):
        """
        Read names of yet unreleased releases from project.yaml file
        """
        if self.project_file == None:
            raise ApplicationError("Project file location not known")

        stream = open(self.project_file, 'r')
        data = yaml.load(stream)

        releases = data["releases"]
        releases = [release for release in releases if release]
        return releases


