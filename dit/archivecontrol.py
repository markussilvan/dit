#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dit-gui

A GUI frontend for Dit issue tracker
"""

import os
import shutil

from ditcontrol import DitControl
from common.errors import ApplicationError
from common.utils import fileutils


class ArchiveControl(object):
    """
    This class handles maintaining archive of the old releases and related issues.
    """
    def __init__(self, dit):
        """
        Initialize.

        Parameters:
        - dit: an initialized DitControl object
        """
        if not isinstance(dit, DitControl):
            raise ApplicationError("Invalid ditcontrol object specified.")
        self.dit = dit

    def archive_release(self, release_name, archive_dir):
        """
        Archive a given release.

        All issues assigned to given release are moved to
        specified archive directory. Current project file
        is copied there to archive the project status.

        Parameters:
        - release_name: name of the release to move to archive
        - archive_dir: directory for archived issues (unique for this release)
        """
        issues = self.dit.get_issues_by_release(release_name, True)
        settings = self.dit.config.get_dit_configs()
        issue_dir = settings.issue_dir
        project_root = self.dit.config.get_project_root()
        #archive_dir = '{}/{}/{}/'.format(project_root, issue_dir, archive_dir)
        archive_dir = os.path.abspath(archive_dir)
        issue_files = []
        for issue in issues:
            issue_file = '{}/{}/issue-{}.yaml'.format(project_root, issue_dir, issue.identifier)
            issue_files.append(issue_file)

        try:
            if os.path.exists(archive_dir) is False:
                os.mkdir(archive_dir)
        except Exception:
            raise ApplicationError("Creating archive directory failed.")

        try:
            fileutils.move_files(issue_files, archive_dir)
        except Exception:
            raise ApplicationError("Archiving release failed. Error moving issue files.")

        project_file = '{}/{}/project.yaml'.format(project_root, issue_dir)
        archive_project_file = '{}/project.yaml'.format(archive_dir)
        #print("DEBUG: copying '{}' to '{}'".format(project_file, archive_project_file))
        try:
            shutil.copy2(project_file, archive_project_file)
        except Exception:
            raise ApplicationError(
                    "Archiving release failed. Error copying project file"
                    "from '{}' to '{}'".format(project_file, archive_project_file))
