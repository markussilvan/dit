#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dit GUI

A GUI frontend for Dit issue tracker
"""

import os
import errno
import datetime

import yaml

from yamlconfig import YamlConfig
from common.items import DitRelease
from common.errors import ApplicationError
from common.utils import fileutils
from common import constants

MOVE_UP = 0
MOVE_DOWN = 1

class ConfigControl(object):
    """
    Dit and dit-gui configuration settings provider
    """
    def __init__(self):
        """
        Initialize.
        """
        self.ditconfig = DitConfigModel()
        self.appconfig = AppConfigModel()
        self.projectconfig = DitProjectModel()

        YamlConfig.add_representers()

    def load_configs(self):
        """
        Cache all configuration variables to memory.

        Raises ApplicationError on failure.
        """
        self.ditconfig.find_config_file()

        if self.ditconfig.read_config_file() is False:
            raise ApplicationError("Reading dit configuration file failed")
        self.appconfig.project_root = self.ditconfig.project_root

        if self.appconfig.read_config_file() is False:
            # using default settings
            pass

        project_file = '{}/{}/{}'.format(self.ditconfig.project_root,
                self.ditconfig.settings.issue_dir, 'project.yaml')
        self.projectconfig.project_file = project_file
        if self.projectconfig.read_config_file() is False:
            raise ApplicationError("Reading project configuration file failed")

    def get_dit_configs(self):
        """
        Return a list of all .dit-config settings.

        Returns:
        - DitConfigYaml object containing all settings
        """
        return self.ditconfig.settings

    def get_app_configs(self):
        """
        Return a list of all .dit-gui-config settings.

        Returns:
        - AppConfigYaml object containing all settings
        """
        return self.appconfig.settings

    def get_project_root(self):
        """
        Get location of project files.

        Returns:
        - absolute path to project files
        """
        return self.ditconfig.project_root

    def get_project_name(self):
        """
        Get project name.

        Returns:
        - project name string
        """
        return self.projectconfig.get_project_name()

    def get_releases(self, status=None, names_only=False):
        """
        Get a list of releases.

        Parameters:
        - status: (optional) release status of releases to list, by default all releases are listed
        - names_only: (optional) list DitReleases or just release names

        Returns:
        - list of unreleased releases
        """
        return self.projectconfig.get_releases(status, names_only)

    def get_issue_directory(self):
        """
        Get absolute path to issues.
        """
        return "{}/{}".format(self.appconfig.project_root, self.ditconfig.settings.issue_dir)

    def get_valid_issue_types(self):
        """
        Get a list of valid types of issues.

        Returns:
        - list of issue types
        """
        return self.appconfig.get_valid_issue_types()

    def get_valid_issue_states(self):
        """
        Get a list of valid states for an issue.

        Returns:
        - list of states
        """
        return self.appconfig.get_valid_issue_states()

    def get_valid_components(self):
        """
        Get a list of valid component names.

        Return:
        - list of component names
        """
        return self.projectconfig.get_components()

    def get_valid_release_states(self):
        """
        Get a list of valid states for a release.

        Returns:
        - list of states
        """
        return self.appconfig.get_valid_release_states()

    def get_default_creator(self):
        """
        Get a string to use as a default creator for issues and release.

        Returns:
        - default creator
        """
        try:
            settings = self.get_dit_configs()
            creator = '{} <{}>'.format(settings.name, settings.email)
        except KeyError:
            return ''
        return creator

    def set_project_root(self, project_root):
        """
        Set location of project files.

        Parameters:
        - absolute path to project files
        """
        self.ditconfig.project_root = project_root

class DitConfigModel:
    """
    Dit configuration file settings provider.
    """
    def __init__(self):
        self.dit_config_file = ".dit-config"
        self.project_root = "."

        # Dit settings from config file
        self.settings = DitConfigYaml("", "", "")

    def find_config_file(self, path="."):
        """
        Find dit configuration file from path toward the root.

        This path is also the project root directory.

        Raises:
        - ApplicationError
        """
        try:
            path = fileutils.find_file_along_path(self.dit_config_file, path)
        except Exception:
            raise ApplicationError("Can't find dit root directory")
        self.project_root = path
        return path

    def read_config_file(self):
        """
        Read settings from dit config file.
        Cache the settings in self.settings (a DitConfigYaml object).

        Returns:
        - True if config file was read successfully
        - False on error, default values set for settings
        """
        config_file = "{}/{}".format(self.project_root, self.dit_config_file)
        try:
            with open(config_file, 'r') as stream:
                self.settings = yaml.load(stream, Loader=yaml.Loader)
        except Exception:
            self.settings = DitConfigYaml("", "", "")
            return False
        return True

    def write_config_file(self):
        """
        Write settings from memory to dit config file.

        Returns:
        - True on success
        - False on any failure
        """
        config_file = "{}/{}".format(self.project_root, self.dit_config_file)
        try:
            with open(config_file, 'w') as stream:
                yaml_data = yaml.dump(self.settings, default_flow_style=False)
                stream.write(yaml_data)
        except Exception:
            return False
        return True


class DitConfigYaml(yaml.YAMLObject):

    yaml_tag = u'!dit.random.org,2008-03-06/config'

    def __init__(self, name, email, issue_dir):
        self.name = name
        self.email = email
        self.issue_dir = issue_dir
        super(DitConfigYaml, self).__init__()

    def __repr__(self):
        return "%s (name=%r, email=%r, issue_dir=%r)" % (self.__class__.__name__,
                self.name, self.email, self.issue_dir)


class AppConfigModel:
    """
    Common configuration settings.
    """
    def __init__(self):
        """
        Initialize AppConfigModel
        """
        self.settings = None
        self.project_root = None
        self.app_config_file = '.dit-gui-config'

    def read_config_file(self):
        """
        Read settings from application config file.
        Cache the settings in self.settings.

        Returns:
        - True on success
        - False on any failure
        """
        config_file = "{}/{}".format(self.project_root, self.app_config_file)
        try:
            with open(config_file, 'r') as stream:
                self.settings = yaml.load(stream, Loader=yaml.Loader)
        except Exception:
            issue_types = ['bugfix', 'feature', 'task', 'enhancement']
            issue_dispositions = ['fixed', "won't fix", 'reorganized', 'invalid']
            self.settings = AppConfigYaml([800, 600], True, "task",
                    issue_types, issue_dispositions)
            return False
        return True

    def write_config_file(self):
        """
        Write settings from memory to dit config file.

        Returns:
        - True on success
        - False on any failure
        """
        config_file = "{}/{}".format(self.project_root, self.app_config_file)
        try:
            with open(config_file, 'w') as stream:
                yaml_data = yaml.dump(self.settings, default_flow_style=False)
                stream.write(yaml_data)
        except Exception:
            return False
        return True

    def get_valid_issue_types(self):
        """
        Get a list of valid types of issues.

        Returns:
        - list of issue types
        """
        return [constants.issue_types.FEATURE,
                constants.issue_types.TASK,
                constants.issue_types.BUGFIX]

    def get_valid_issue_states(self):
        """
        Get a list of valid states for an issue.

        Returns:
        - list of states
        """
        return [constants.issue_states.UNSTARTED,
                constants.issue_states.IN_PROGRESS,
                constants.issue_states.PAUSED]

    def get_valid_release_states(self):
        """
        Get a list of valid states for a release.

        Returns:
        - list of states
        """
        states = [constants.release_states.UNRELEASED, constants.release_states.RELEASED]
        return states


class AppConfigYaml(yaml.YAMLObject):

    yaml_tag = u'!dit.random.org,2008-03-06/guiconfig'

    def __init__(self, window_size, remember_window_size, default_issue_type,
            issue_types, issue_dispositions):
        self.window_size = window_size
        self.remember_window_size = remember_window_size
        self.default_issue_type = default_issue_type
        self.issue_types = issue_types
        self.issue_dispositions = issue_dispositions
        super(AppConfigYaml, self).__init__()

    def __repr__(self):
        return ("%s (window_size=%r, remember_window_size=%r, default_issue_type=%r,"
                "issue_types=%r, issue_dispositions=%r)") % (
                self.__class__.__name__, self.window_size, self.remember_window_size,
                self.default_issue_type, self.issue_types, self.issue_dispositions)


class DitProjectModel:
    """
    Dit project file content provider.
    """
    def __init__(self, project_file=None):
        """
        Initialize DitProjectModel.
        """
        self.project_file = project_file
        self.project_data = DitProjectYaml("", [], ["ui","core", "tests"], "0.5")

    def read_config_file(self):
        """
        Read all project information from project.yaml file.

        Returns:
        - True on success
        - False on failure
        """
        if self.project_file is None:
            return False
        try:
            with open(self.project_file, 'r') as stream:
                self.project_data = yaml.load(stream, Loader=yaml.Loader)
        except Exception:
            return False
        return True

    def write_config_file(self):
        """
        Write all project information to project.yaml file.

        Returns:
        - True on success
        - False on failure or invalid parameters
        """
        if self.project_file is None or self.project_data is None:
            return False

        try:
            project_dir = os.path.dirname(self.project_file)
            os.makedirs(project_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                #raise ApplicationError("Creating issue directory failed")
                return False
        try:
            with open(self.project_file, 'w') as stream:
                yaml_data = yaml.dump(self.project_data, default_flow_style=False)
                stream.write(yaml_data)
        except Exception:
            return False
        return True

    def get_project_name(self):
        """
        Read project name from config file.

        Returns:
        - project name
        """
        if self.project_file is None:
            return None
        if self.project_data is None:
            self.read_config_file()
        return self.project_data.name

    def get_components(self):
        """
        Read project component configuration from config file.
        Returns:
        - list of components
        """
        if self.project_file is None:
            return None
        if self.project_data is None:
            self.read_config_file()
        return self.project_data.components

    def add_component(self, component_name):
        """
        Add a new component to the project configuration.

        Parameters:
        - name of the component to add
        """
        if self.project_file is None:
            return None
        if self.project_data is None:
            self.read_config_file()
        if self.project_data.components is None:
            self.project_data.components = []
        self.project_data.components.append(component_name)

    def remove_component(self, component_name):
        """
        Remove a component from the project configuration.

        Parameters:
        - name of the component to remove
        """
        if self.project_file is None:
            return None
        if self.project_data is None:
            self.read_config_file()
        if self.project_data.components is None:
            self.project_data.components = []
        self.project_data.components.remove(component_name)

    def get_releases(self, status=None, names_only=False):
        """
        Read releases from Dit project.yaml file.
        Config file must be read first, or the settings set by other means,
        so we can know where the file can be found. If project file is not
        read, then it is read first, if the path to the project root is known.

        Parameters:
        - status: (optional) release status of releases to list, by default all releases are listed
        - names_only: (optional) list DitReleases or just release names

        Returns:
        - list of DitRelease objects or release names
        """
        if self.project_file is None:
            return None
        if self.project_data is None:
            self.read_config_file()
        status = self._string_to_release_status(status)
        if names_only is True:
            if status is not None:
                releases = [release["name"] for release in self.project_data.releases
                        if release["status"] == status]
            else:
                releases = [release["name"] for release in self.project_data.releases]
        else:
            if status is not None:
                releases_data = [release for release in self.project_data.releases
                        if release["status"] == status]
            else:
                releases_data = [release for release in self.project_data.releases]
            releases = []
            for rel in releases_data:
                status = self._release_status_to_string(rel['status'])
                release = DitRelease(rel['name'], 'Release', status,
                    rel['release_time'], rel['log_events'])
                releases.append(release)

        return releases

    def set_release(self, release, old_name=None):
        """
        Add or update information of a release to project.

        Parameters:
        - release: a DitRelease to update
        - old_name: (optional) old name of the release being updated
        """
        if not isinstance(release, DitRelease):
            return False
        if not isinstance(release.title, str):
            return False

        # search for this release in current project data
        if old_name:
            if not isinstance(old_name, str):
                return False
            title = old_name
        else:
            title = release.title
        release_data = None
        for rel in self.project_data.releases:
            if rel["name"] == title:
                release_data = rel
                break

        if old_name and not release_data:
            # given parameters indicate rename, but such release is not found
            return False

        if release_data:
            release_data['name'] = release.title
            release_data['status'] = self._string_to_release_status(release.status)
            release_data['release_time'] = release.release_time_as_string()
            release_data['log_events'] = release.log
        else:
            status = self._string_to_release_status(release.status)
            release_yaml = DitReleaseYaml(release.title, status,
                    release.release_time_as_string(), release.log)
            self.project_data.releases.append(release_yaml)
        return True

    def make_release(self, release: DitRelease):
        """
        Release a release.

        Parameters:
        - release: release (a DitRelease) to release
        """
        if release is None:
            return False
        if self.project_data is None:
            return False

        release_data = None
        for rel in self.project_data.releases:
            if rel["name"] == release.title:
                release_data = rel
                break

        if release_data:
            release_data['status'] = self._string_to_release_status(constants.release_states.RELEASED)
            release.release_time = datetime.datetime.now(datetime.timezone.utc)
            release_data['release_time'] = release.release_time_as_string()
            release_data['log_events'] = release.log
            return True
        return False

    def remove_release(self, release_name):
        """
        Remove a release from the project.

        Even if release contains issues, it's still removed.
        Issues are left as they were.

        Parameters:
        - release_name: name of the release to remove

        Returns:
        - True if release was removed
        - False if release was not found
        """
        for rel in self.project_data.releases:
            if rel["name"] == release_name:
                self.project_data.releases.remove(rel)
                return True
        return False

    def move_release(self, release_name, direction):
        """
        Move release up or down changing its place in the queue.

        Releases position can be considered its priority.

        Parameters:
        - release_name: name of the release to remove
        - direction: MOVE_UP (higher priority) or MOVE_DOWN (lower priority)

        Returns:
        - True if release was moved
        - False if release was not found
        """
        if self.project_data is None:
            return False
        for rel in self.project_data.releases:
            if rel["name"] == release_name:
                rels = self.project_data.releases
                current = rels.index(rel)
                if direction == MOVE_UP:
                    if current > 0:
                        rels[current-1], rels[current] = rels[current], rels[current-1]
                        return True
                    else:
                        return False
                elif direction == MOVE_DOWN:
                    if current < len(rels) - 1:
                        rels[current+1], rels[current] = rels[current], rels[current+1]
                        return True
                    else:
                        return False
        return False

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
        return None

    def _string_to_release_status(self, status):
        """
        Convert a readable string to a YAML release status.

        Readable format is used in internal objects.
        YAML objects use different format with underscores
        and a ':' prefix.

        Parameters:
        - status: readable release status string

        Returns:
        - YAML release status
        """
        if status:
            return ':' + status
        return None


class DitProjectYaml(yaml.YAMLObject):

    yaml_tag = u'!dit.random.org,2008-03-06/project'

    def __init__(self, name, releases, components, version):
        self.name = name
        self.releases = releases
        self.components = components
        self.version = version
        super(DitProjectYaml, self).__init__()

    def __repr__(self):
        return "%s (name=%r, releases=%r, components=%r, version=%r)" % (
                self.__class__.__name__, self.name, self.releases,
                self.components, self.version)

    #def __getitem__(self, key):
    #    return eval("self.{}".format(key))

    #def __setitem__(self, key, item):
    #    eval("self.{} = item".format(key))

class DitComponentYaml(yaml.YAMLObject):

    yaml_tag = u'!dit.random.org,2008-03-06/component'

    def __init__(self, name):
        self.name = name
        super(DitComponentYaml, self).__init__()

    def __repr__(self):
        return "%s (name=%r)" % (
                self.__class__.__name__, self.name)


class DitReleaseYaml(yaml.YAMLObject):

    yaml_tag = u'!dit.random.org,2008-03-06/release'

    def __init__(self, name, status, release_time, log):
        self.name = name
        self.status = status
        self.release_time = release_time
        self.log_events = log
        super(DitReleaseYaml, self).__init__()

    def __repr__(self):
        return "%s (name=%r, status=%r, release_time=%r)" % (
                self.__class__.__name__, self.name, self.status, self.release_time)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value
