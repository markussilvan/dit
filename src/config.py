#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker
"""

import yaml

from common.items import DitzRelease
from common.errors import ApplicationError
from common.utils import fileutils
from common.unused import unused

class ConfigControl(object):
    """
    Ditz and ditz-gui configuration settings provider
    """
    def __init__(self):
        """
        Initialize
        """
        self.ditzconfig = DitzConfigModel()
        self.appconfig = AppConfigModel()
        self.projectconfig = DitzProjectModel()

    def load_configs(self):
        """
        Cache all configuration variables to memory
        """
        self.ditzconfig.read_config_file()
        self.appconfig.project_root = self.ditzconfig.project_root
        self.appconfig.read_config_file()
        project_file = '{}/{}/{}'.format(self.ditzconfig.project_root,
                self.ditzconfig.settings.issue_dir, 'project.yaml')
        self.projectconfig.project_file = project_file
        self.projectconfig.read_config_file()

    def get_ditz_configs(self):
        """
        Return a list of all .ditz-config settings

        Returns:
        - DitzConfigYaml object containing all settings
        """
        return self.ditzconfig.settings

    def get_app_configs(self):
        """
        Return a list of all .ditz-gui-config settings

        Returns:
        - AppConfigYaml object containing all settings
        """
        return self.appconfig.settings

    def get_project_name(self):
        """
        Get project name

        Returns:
        - project name string
        """
        return self.projectconfig.get_project_name()

    def get_releases(self, status=None, names_only=False):
        """
        Get a list of releases

        Parameters:
        - status: (optional) release status of releases to list, by default all releases are listed
        - names_only: (optional) list DitzReleases or just release names

        Returns:
        - list of unreleased releases
        """
        return self.projectconfig.get_releases(status, names_only)

    def get_valid_issue_states(self):
        """
        Get a list of valid states for an issue

        Returns:
        - list of states
        """
        return self.appconfig.get_valid_issue_states()

    def get_valid_issue_types(self):
        """
        Get a list of valid issue types for an issue

        Returns:
        - list of issue types
        """
        return self.appconfig.get_valid_issue_types()

    def get_valid_issue_dispositions(self):
        """
        Get a list of valid issue dispositions for an issue

        Returns:
        - list of issue dispositions
        """
        return self.appconfig.get_valid_issue_dispositions()

    def get_valid_release_states(self):
        """
        Get a list of valid states for a release

        Returns:
        - list of states
        """
        return self.appconfig.get_valid_release_states()


class DitzConfigModel(object):
    """
    Ditz configuration file settings provider
    """
    def __init__(self):
        self.ditz_config_file = ".ditz-config"
        self.project_root = None

        # Ditz settings from config file
        self.settings = None

        self.find_ditz_config()

    def find_ditz_config(self, path="."):
        """
        Find ditz configuration file from path toward the root.

        This path is also the project root directory.

        Raises:
        - ApplicationError
        """
        try:
            path = fileutils.find_file_along_path(self.ditz_config_file, path)
        except Exception:
            raise ApplicationError("Can't find ditz root directory")
        self.project_root = path
        return path

    def read_config_file(self):
        """
        Read settings from ditz config file
        Cache the settings in self.settings.

        Returns:
        - a DitzConfigYaml object containing settings
        """
        config_file = "{}/{}".format(self.project_root, self.ditz_config_file)
        with open(config_file, 'r') as stream:
            self.settings = yaml.load(stream)
            return self.settings
        raise ApplicationError("Error reading ditz settings file")

    def write_config_file(self):
        """
        Write settings from memory to ditz config file.
        """
        config_file = "{}/{}".format(self.project_root, self.ditz_config_file)
        try:
            with open(config_file, 'w') as stream:
                yaml_data = yaml.dump(self.settings, default_flow_style=False)
                stream.write(yaml_data)
        except Exception:
            raise ApplicationError("Error writing ditz settings file")


class DitzConfigYaml(yaml.YAMLObject):

    yaml_tag = u'!ditz.rubyforge.org,2008-03-06/config'

    def __init__(self, name, email, issue_dir):
        self.name = name
        self.email = email
        self.issue_dir = issue_dir
        super(DitzConfigYaml, self).__init__()

    def __repr__(self):
        return "%s (name=%r, email=%r, issue_dir=%r)" % (self.__class__.__name__,
                self.name, self.email, self.issue_dir)

    #def __getitem__(self,):
    #    return sel
    #def __setitem__(self, key, item):
    #    self.data[key] = item


class AppConfigModel(object):
    """
    Common configuration settings
    """
    def __init__(self):
        """
        Initialize AppConfigModel
        """
        self.settings = None
        self.project_root = None
        self.app_config_file = '.ditz-gui-config'

    def read_config_file(self):
        """
        Read settings from application config file
        Cache the settings in self.settings.

        Returns:
        - a YamlAppConfig object containing settings
        """
        config_file = "{}/{}".format(self.project_root, self.app_config_file)
        with open(config_file, 'r') as stream:
            self.settings = yaml.load(stream)
            return self.settings
        raise ApplicationError("Error reading application settings file")

    def write_config_file(self):
        """
        Write settings from memory to ditz config file.
        """
        config_file = "{}/{}".format(self.project_root, self.app_config_file)
        try:
            with open(config_file, 'w') as stream:
                yaml_data = yaml.dump(self.settings, default_flow_style=False)
                stream.write(yaml_data)
        except Exception:
            raise ApplicationError("Error writing application configuration file")

    def get_valid_issue_states(self):
        """
        Get a list of valid states for an issue

        Returns:
        - list of states
        """
        return ["unstarted", "in progress", "paused"]

    def get_valid_issue_types(self):
        """
        Get a list of valid issue types for an issue

        Returns:
        - list of issue types
        """
        return ["bugfix", "feature", "task"]

    def get_valid_issue_dispositions(self):
        """
        Get a list of valid issue dispositions for an issue

        Returns:
        - list of issue dispositions
        """
        return ["fixed", "won't fix", "reorganized"]

    def get_valid_release_states(self):
        """
        Get a list of valid states for a release

        Returns:
        - list of states
        """
        return ["unreleased", "released"]


class AppConfigYaml(yaml.YAMLObject):

    yaml_tag = u'!ditz.rubyforge.org,2008-03-06/guiconfig'

    def __init__(self, window_size, default_issue_type):
        self.window_size = window_size
        self.default_issue_type = default_issue_type
        super(AppConfigYaml, self).__init__()

    def __repr__(self):
        return "%s (window_size=%r, remember_window_size=%r, default_issue_type=%r)" % (
                self.__class__.__name__, self.window_size, self.remember_window_size,
                self.default_issue_type)


class DitzProjectModel(object):
    """
    Ditz project file content provider
    """
    def __init__(self, project_file=None):
        """
        Initialize DitzProjectModel.
        """
        self.project_file = project_file
        self.project_data = None

    def read_config_file(self):
        """
        Read all project information from project.yaml file
        """
        if self.project_file == None:
            return None
        writer = DitzProjectWriter(self.project_file)
        self.project_data = writer.read_config_file()
        return self.project_data

    def write_config_file(self):
        """
        Read all project information to project.yaml file
        """
        if self.project_file == None or self.project_data == None:
            return None
        writer = DitzProjectWriter(self.project_file)
        return writer.write_config_file(self.project_data)

    def get_project_name(self):
        """
        Read project name from config file

        Returns:
        - project name
        """
        if self.project_file == None:
            return None
        if self.project_data == None:
            self.read_config_file()
        return self.project_data["name"]

    def get_releases(self, status=None, names_only=False):
        """
        Read releases from Ditz project.yaml file.
        Config file must be read first, or the settings set by other means,
        so we can know where the file can be found. If project file is not
        read, then it is read first, if the path to the project root is known.

        Parameters:
        - status: (optional) release status of releases to list, by default all releases are listed
        - names_only: (optional) list DitzReleases or just release names

        Returns:
        - list of DitzRelease objects or release names
        """
        if self.project_file == None:
            return None
        if self.project_data == None:
            self.read_config_file()
        status = self._string_to_release_status(status)
        if names_only == True:
            if status != None:
                releases = [release["name"] for release in self.project_data["releases"]
                        if release["status"] == status]
            else:
                releases = [release["name"] for release in self.project_data["releases"]]
        else:
            if status != None:
                releases_data = [release for release in self.project_data["releases"]
                        if release["status"] == status]
            else:
                releases_data = [release for release in self.project_data["releases"]]
            releases = []
            for rel in releases_data:
                status = self._release_status_to_string(rel['status'])
                release = DitzRelease(rel['name'], 'Release', status,
                    rel['release_time'], rel['log_events'])
                releases.append(release)

        return releases

    def set_release(self, release):
        """
        Add or update information of a release to project.

        Parameters:
        - release: a DitzRelease to update
        """
        if release.title in self.project_data["releases"]:
            release_data = [rel for rel in self.project_data["releases"]
                    if rel["name"] == release.title]
            release_data['name'] = release.title
            release_data['status'] = self._string_to_release_status(release.status)
            release_data['release_time'] = release.release_time
            release_data['log_events'] = release.log
        else:
            release_data = {}
            release_data['name'] = release.title
            release_data['status'] = self._string_to_release_status(release.status)
            release_data['release_time'] = release.release_time
            release_data['log_events'] = release.log
            self.project_data["releases"].append(release_data)

    def _release_status_to_string(self, status):
        """
        Convert yaml release status to a readable string.

        Parameters:
        - status: yaml release status

        Returns:
        - release status as readable string
        """
        if status:
            return status[1:]
        else:
            return None

    def _string_to_release_status(self, status):
        """
        Convert a readable string to a YAML release status.

        Parameters:
        - status: readable release status string

        Returns:
        - YAML release status
        """
        if status:
            return ':' + status
        else:
            return None


class DitzProjectWriter():
    """
    A class to read and write Ditz project.yaml file
    """
    def __init__(self, project_file):
        self.project_file = project_file

        yaml.add_constructor(u"!ditz.rubyforge.org,2008-03-06/project", self.ditz_project)
        yaml.add_constructor(u"!ditz.rubyforge.org,2008-03-06/component", self.ditz_component)
        yaml.add_constructor(u"!ditz.rubyforge.org,2008-03-06/release", self.ditz_project)

    def ditz_project(self, loader, node):
        #--- !ditz.rubyforge.org,2008-03-06/project
        return loader.construct_yaml_map(node)

    def ditz_component(self, loader, node):
        #--- !ditz.rubyforge.org,2008-03-06/component
        unused(loader)
        unused(node)
        return ""

    def read_config_file(self):
        """
        Read all project information from project.yaml file
        """
        if self.project_file == None:
            raise ApplicationError("Project file location not known")

        with open(self.project_file, 'r') as stream:
            return yaml.load(stream)
        raise ApplicationError("Error reading project settings file")

    def write_config_file(self, settings):
        """
        Read all project information to project.yaml file

        Parameters:
        - settings: project settings to write to the file
        """
        if self.project_file == None:
            raise ApplicationError("Project file location not known")

        try:
            with open(self.project_file, 'w') as stream:
                yaml_data = yaml.dump(settings, default_flow_style=False)
                stream.write(yaml_data)
        except Exception:
            raise ApplicationError("Error writing project configuration file")

