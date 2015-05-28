#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker
"""

import shutil

from common.errors import ApplicationError
from common.utils import fileutils


class ArchiveControl(object):
    """
    This class handles maintaining archive of the old releases and related issues.
    """
    def __init__(self, ditz):
        """
        Initialize.

        Parameters:
        - ditz: an initialized DitzControl object
        """
        self.ditz = ditz

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
        issues = self.ditz.get_issues_by_release(release_name, True)
        settings = self.ditz.config.get_ditz_configs()
        issue_dir = settings.issue_dir
        project_root = self.ditz.config.get_project_root()
        #archive_dir = '{}/{}/{}/'.format(project_root, issue_dir, archive_dir)
        issue_files = []
        for issue in issues:
            issue_file = '{}/{}/issue-{}.yaml'.format(project_root, issue_dir, issue.identifier)
            issue_files.append(issue_file)

        try:
            fileutils.move_files(issue_files, archive_dir)
        except Exception:
            raise ApplicationError("Archiving release failed. Error moving issue files.")

        project_file = '{}/{}/project.yaml'.format(project_root, issue_dir)
        try:
            shutil.copy2(project_file, '{}/project.yaml'.format(archive_dir))
        except Exception:
            raise ApplicationError("Archiving release failed. Error copying project file.")


