#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker
"""

import datetime

from itemcache import ItemCache
from common.items import DitzRelease
from common.errors import ApplicationError, DitzError
from common.utils.issue import IssueUtils
from yamlcontrol import IssueYamlControl, IssueYamlObject
from config import ConfigControl


class DitzControl(object):
    """
    This class handles communication to Ditz command line interface.
    Ditz issue data is read using the Ditz command line tool.
    """
    def __init__(self, config):
        """
        Initialize

        Parameters:
        - config: ConfigControl object containing valid configuration values
        """
        self.ditz_cmd = "ditz"
        self.issuecontrol = IssueYamlControl()
        self.item_cache = ItemCache()
        if not isinstance(config, ConfigControl):
            raise ApplicationError('Construction failed due to invalid config parameter')
        self.config = config
        self.reload_cache()

    def reload_cache(self):
        """
        Get basic information for all issues in the system.
        Cache that information to memory.
        """
        # (re)create the cache
        self.item_cache.clear()
        identifiers = self.issuecontrol.list_issue_identifiers()
        for issue_id in identifiers:
            ditz_item = self.get_issue_content(issue_id, False)
            self.item_cache.add_issue(ditz_item)
        self.item_cache.sort_issues(rename = True)

        releases = self.config.get_unreleased_releases()
        for title in releases:
            self.item_cache.add_release(DitzRelease(title, 'Release'))
        self.item_cache.sort_releases()

    def get_items(self):
        """
        Get a list of all releases and issues stored in Ditz.
        Returned list is sorted by releases.

        Returns:
        - A list of DitzItems
        """
        items = []
        self.reload_cache()

        for release in self.item_cache.releases:
            items.append(release)
            issues = self.item_cache.get_issues_by_release(release.title)
            issues = IssueUtils.sort_issues_by_status(issues)
            items.extend(issues)

        # add unassigned items
        items.append(DitzRelease('Unassigned'))
        issues = self.item_cache.get_issues_by_release(None)
        issues = IssueUtils.sort_issues_by_status(issues)
        items.extend(issues)

        return items

    def get_issue_status_by_ditz_id(self, ditz_id):
        """
        Get status of an Ditz issue loaded in the cached list of issues.

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue

        Returns:
        - issue status
        - None if requested issue is not found
        """
        return self.item_cache.get_issue_status_by_id(ditz_id)

    def get_issue_from_cache(self, ditz_id):
        """
        Get DitzIssue from cache by Ditz identifier or name.

        Parameters:
        - ditz_id: Ditz name or identifier of an issue

        Returns:
        - DitzIssue object
        - None if requested item is not found
        """
        return self.item_cache.get_issue(ditz_id)

    def get_issue_identifier(self, issue_name):
        """
        Get SHA identifier of a given issue.

        Parameters:
        - issue_name: name of the issue

        Returns:
        - issue identifier
        """
        issue = self._get_issue_by_id(issue_name)
        if issue:
            return issue.identifier
        return None

    def get_issue_content(self, identifier, update_cache=True):
        """
        Get all content of one issue from storage by its identifier hash.

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue
        - update_cache: (optional) flag to show if issue cache content
                        should be updated

        Returns:
        - A Ditz item object filled with information of that issue
        - None if ditz_id is invalid
        """
        if identifier == None or identifier == "":
            return None
        if len(identifier) != 40:
            # issue name given instead?
            issue = self._get_issue_by_id(identifier)
            if issue:
                identifier = issue.identifier
            if identifier and len(identifier) != 40:
                return None
        yaml_issue = self.issuecontrol.read_issue_yaml(identifier)
        ditz_item = yaml_issue.toDitzIssue()
        if update_cache:
            self.item_cache.add_issue(ditz_item)
            #self.item_cache.sort_issues(rename = True)
        return ditz_item

    def add_issue(self, issue, comment=''):
        """
        Add new issue to Ditz
        Ditz also asks for a comment when an issue is added,
        but saving a comment is not supported.

        Parameters:
        - issue: a DitzIssue filled with data to save
        - comment: (optional) comment to add to the issue's event log
        """
        if issue.identifier != None and issue.identifier != "":
            raise DitzError("Issue has an identifier, not a new issue?")

        if issue.created == None:
            issue.created = datetime.datetime.utcnow()
        if issue.component == None:
            issue.component = self.config.get_project_name()

        issue.identifier = self.issuecontrol.generate_new_identifier()
        self._add_issue_log_entry(issue, 'created', comment)

        yaml_issue = IssueYamlObject.fromDitzIssue(issue)
        self.issuecontrol.write_issue_yaml(yaml_issue)

    def edit_issue(self, issue, comment=''):
        """
        Modify an existing Ditz issue.
        Ditz also asks for a comment when an issue is edited,
        but saving a comment is not supported.

        Parameters:
        - issue: a DitzIssue filled with data to save
        - comment: (optional) comment to add to the issue's event log
        """
        if issue.identifier == None or issue.identifier == "":
            raise DitzError("Issue has no identifier")

        self._add_issue_log_entry(issue, 'edited', comment)

        yaml_issue = IssueYamlObject.fromDitzIssue(issue)
        self.issuecontrol.write_issue_yaml(yaml_issue)

    def add_comment(self, ditz_id, comment):
        """
        Write a new comment to a Ditz item

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue to close
        - comment: (optional) comment text, no formatting, to add to the closed issue
        """
        if ditz_id == None or ditz_id == "":
            raise DitzError("Invalid ditz issue identifier")
        if comment == None or comment == "":
            raise DitzError("Missing comment")

        ditz_issue = self._get_issue_by_id(ditz_id)
        self._add_issue_log_entry(ditz_issue, 'commented', comment)

        yaml_issue = IssueYamlObject.fromDitzIssue(ditz_issue)
        self.issuecontrol.write_issue_yaml(yaml_issue)

    def add_reference(self, ditz_id, reference, comment=""):
        """
        Add a new reference to a Ditz item

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue
        - reference: reference to add to the issue
        - comment: comment text, if any comment should be added
        """
        if ditz_id == None or ditz_id == "":
            raise DitzError("Invalid ditz issue identifier")
        if reference == None or reference == "":
            raise DitzError("Invalid reference")

        ditz_issue = self._get_issue_by_id(ditz_id)
        ditz_issue.references.append(reference)
        self._add_issue_log_entry(ditz_issue, 'added reference', comment)

        yaml_issue = IssueYamlObject.fromDitzIssue(ditz_issue)
        self.issuecontrol.write_issue_yaml(yaml_issue)

    def _disposition_to_str(self, disposition):
        """
        Convert disposition numerical (index) value to string

        Parameters:
        - disposition: disposition (numeric)

        Returns:
        - disposition as string
        """
        dispositions = self.config.get_valid_issue_dispositions()
        return dispositions[disposition-1]

    def close_issue(self, ditz_id, disposition, comment=""):
        """
        Close an existing Ditz item

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue to close
        - disposition: 1) fixed, 2) won't fix, 3) reorganized
        - comment: (optional) comment text, no formatting, to add to the closed issue
        """
        if ditz_id == None or ditz_id == "":
            raise ApplicationError("Invalid ditz item identifier")
        if disposition < 1 or disposition > 3:
            raise ApplicationError("Invalid disposition value")

        ditz_issue = self._get_issue_by_id(ditz_id)
        ditz_issue.status = 'closed'
        ditz_issue.disposition = self._disposition_to_str(disposition)
        action = "closed with disposition {}".format(disposition)
        self._add_issue_log_entry(ditz_issue, action, comment)

        yaml_issue = IssueYamlObject.fromDitzIssue(ditz_issue)
        self.issuecontrol.write_issue_yaml(yaml_issue)

    def drop_issue(self, identifier):
        """
        Remove an existing Ditz issue.

        The data is lost forever when an issue is dropped.

        Parameters:
        - identifier: Ditz hash or name identifier of an issue to drop

        Raises:
        - DitzError if running Ditz command fails
        """
        if identifier == None or identifier == "":
            return
        if len(identifier) != 40:
            # issue name given instead?
            issue = self._get_issue_by_id(identifier)
            if issue:
                identifier = issue.identifier
            if identifier and len(identifier) != 40:
                return None
        try:
            self.issuecontrol.remove_issue_yaml(identifier)
            self.item_cache.remove_issue(identifier)
        except DitzError, e:
            e.error_message = "Dropping issue failed"
            raise

    def assign_issue(self, ditz_id, release, comment=''):
        """
        Assign a Ditz issue to a release

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue
        - release: which release to assign the issue
        - comment: (optional) comment text, no formatting, to add to the issue

        Raises:
        - DitzError if running Ditz command fails
        """
        ditz_issue = self._get_issue_by_id(ditz_id)
        old_release = ditz_issue.release
        ditz_issue.release = release
        if old_release == None or old_release == '':
            old_release = 'Unassigned'

        action = "assigned to release {} from {}".format(release, old_release)
        self._add_issue_log_entry(ditz_issue, action, comment)

        yaml_issue = IssueYamlObject.fromDitzIssue(ditz_issue)
        self.issuecontrol.write_issue_yaml(yaml_issue)

    def start_work(self, ditz_id, comment=''):
        """
        Start working on an Ditz issue

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue
        - comment: (optional) comment text, no formatting, to add to the issue

        Raises:
        - DitzError if running Ditz command fails
        """
        self._change_issue_status(ditz_id, 'in progress', comment)

    def stop_work(self, ditz_id, comment=''):
        """
        Stop working on an Ditz issue

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue
        - comment: (optional) comment text, no formatting, to add to the issue
        """
        self._change_issue_status(ditz_id, 'paused', comment)

    def make_release(self, release_name, comment):
        """
        Release a release

        Parameters:
        - release_name: Name of a release in Ditz
        - comment: (optional) comment text, no formatting, to add to the release
        """
        if release_name == None or release_name == "":
            return
        #try:
        #    self._run_interactive_command("release " + release_name, comment, "/stop")
        #except DitzError, e:
        #    e.error_message = "Making release on Ditz failed"
        #    raise

    def _change_issue_status(self, ditz_id, status, comment=''):
        """
        Change Ditz issue status.

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue
        - status: new status to set for the issue
        - comment: (optional) comment text, no formatting, to add to the issue

        Raises:
        - DitzError if running Ditz command fails
        """
        if ditz_id == None or ditz_id == "":
            return
        if status == None or status == "":
            return

        ditz_issue = self._get_issue_by_id(ditz_id)
        old_status = ditz_issue.status
        ditz_issue.status = status
        ditz_issue.disposition = None
        action = "status changed from {} to {}".format(old_status, status)
        self._add_issue_log_entry(ditz_issue, action, comment)

        yaml_issue = IssueYamlObject.fromDitzIssue(ditz_issue)
        self.issuecontrol.write_issue_yaml(yaml_issue)

    def _get_issue_by_id(self, ditz_id):
        """
        Get DitzIssue from cache or file.

        Parameters:
        - ditz_id: issue hash identifier or name
        """
        if ditz_id == None or ditz_id == "":
            raise ApplicationError("Invalid ditz item identifier")

        ditz_issue = self.get_issue_from_cache(ditz_id)
        if not ditz_issue and len(ditz_id) == 40:
            # try to load issue in case it exists, but is not cached
            ditz_issue = self.get_issue_content(ditz_id)
            if not ditz_issue:
                raise ApplicationError('Unable to find issue: {}'.format(ditz_id))
            self.reload_cache()

            # use the cached issue to keep cache up to date
            ditz_issue = self.get_issue_from_cache(ditz_id)
            if not ditz_issue:
                raise ApplicationError('Unable to find issue even after reload: {}'.format(ditz_id))

        return ditz_issue

    def _add_issue_log_entry(self, issue, action, comment=None):
        """
        Add a new log entry to an issue

        Parameters:
        - issue: issue to which to add the change
        - action: title describing what was done
        - comment: (optional) a comment to the log, empty by default
        """
        settings = self.config.get_ditz_configs()
        creator = '{} <{}>'.format(settings.name, settings.email)
        issue.add_log_entry(None, action, creator, comment)


