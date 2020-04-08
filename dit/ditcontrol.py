#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dit GUI

A GUI frontend for Dit issue tracker
"""

import datetime

from config import ConfigControl
from itemcache import ItemCache
from common.items import DitRelease
from common.errors import ApplicationError, DitError
from common.utils.issue import IssueUtils
from common import constants
from issuemodel import IssueModel, IssueYamlObject


class DitControl(object):
    """
    This class handles communication to Dit command line interface.
    Dit issue data is read using the Dit command line tool.
    """
    def __init__(self, config):
        """
        Initialize

        Parameters:
        - config: ConfigControl object containing valid configuration values
        """
        if not isinstance(config, ConfigControl):
            raise ApplicationError('Construction failed due to invalid config parameter')
        self.config = config
        self.issuemodel = IssueModel(self.config.get_issue_directory())
        self.item_cache = ItemCache()
        self.reload_cache()

    def reload_cache(self):
        """
        Get basic information for all issues in the system.
        Cache that information to memory.
        """
        # (re)create the cache
        self.item_cache.clear()
        identifiers = self.issuemodel.list_issue_identifiers()
        for issue_id in identifiers:
            dit_item = self.get_issue_content(issue_id, False)
            self.item_cache.add_issue(dit_item)
        self.item_cache.sort_issues(rename=True)

        releases = self.config.get_releases(constants.release_states.UNRELEASED)
        if releases:
            for release in releases:
                self.item_cache.add_release(release)
            self.item_cache.sort_releases()

    def get_items(self):
        """
        Get a list of all releases and issues stored in Dit.
        Returned list is sorted by releases.

        Returns:
        - A list of DitItems
        """
        items = []
        self.reload_cache()

        for release in self.item_cache.releases:
            items.append(release)
            issues = self.item_cache.get_issues_by_release(release.title)
            issues = IssueUtils.sort_issues_by_status(issues)
            items.extend(issues)

        # add unassigned items
        items.append(DitRelease(constants.releases.UNASSIGNED))
        issues = self.item_cache.get_issues_by_release(None)
        issues = IssueUtils.sort_issues_by_status(issues)
        items.extend(issues)

        return items

    def get_issue_status_by_dit_id(self, dit_id):
        """
        Get status of an Dit issue loaded in the cached list of issues.

        Parameters:
        - dit_id: Dit hash or name identifier of an issue

        Returns:
        - issue status
        - None if requested issue is not found
        """
        return self.item_cache.get_issue_status_by_id(dit_id)

    def get_issue_from_cache(self, dit_id):
        """
        Get DitIssue from cache by Dit identifier or name.

        Parameters:
        - dit_id: Dit name or identifier of an issue

        Returns:
        - DitIssue object
        - None if requested item is not found
        """
        return self.item_cache.get_issue(dit_id)

    def get_release_from_cache(self, release):
        """
        Get DitRelease from cache by release name.

        Parameters:
        - release: name of the release

        Returns:
        - DitRelease object
        - None if requested release is not found
        """
        return self.item_cache.get_release(release)

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
        - dit_id: Dit hash or name identifier of an issue
        - update_cache: (optional) flag to show if issue cache content
                        should be updated

        Returns:
        - A Dit item object filled with information of that issue
        - None if dit_id is invalid
        """
        if identifier in (None, ""):
            return None
        if len(identifier) != 40:
            # issue name given instead?
            issue = self._get_issue_by_id(identifier)
            if issue:
                identifier = issue.identifier
            if identifier and len(identifier) != 40:
                return None
        yaml_issue = self.issuemodel.read_issue_yaml(identifier)
        dit_item = yaml_issue.to_dit_issue()
        if update_cache:
            self.item_cache.add_issue(dit_item)
            #self.item_cache.sort_issues(rename = True)
        return dit_item

    def get_issue_name_max_len(self):
        """
        Get length of the longest issue name found in cache

        Returns:
        - length of longest issue name as integer
        """
        return self.item_cache.get_issue_name_max_len()

    def get_issues_by_release(self, release_name, include_closed=False):
        """
        Get all issues from cache assigned to a given release.

        Parameters:
        - release_name: name of the release
        - include_closed: list also closed tasks

        Returns:
        - list of DitIssues
        """
        return self.item_cache.get_issues_by_release(release_name, include_closed)

    def add_issue(self, issue, comment=''):
        """
        Add new issue to Dit
        Dit also asks for a comment when an issue is added,
        but saving a comment is not supported.

        Parameters:
        - issue: a DitIssue filled with data to save
        - comment: (optional) comment to add to the issue's event log
        """
        if issue.identifier not in (None, ""):
            raise DitError("Issue has an identifier, not a new issue?")

        if issue.created is None:
            issue.created = datetime.datetime.utcnow()
        if issue.component is None:
            issue.component = self.config.get_project_name()

        issue.identifier = self.issuemodel.generate_new_identifier()
        self._add_issue_log_entry(issue, 'created', comment)

        yaml_issue = IssueYamlObject.from_dit_issue(issue)
        self.issuemodel.write_issue_yaml(yaml_issue)

    def edit_issue(self, issue, comment=''):
        """
        Modify an existing Dit issue.
        Dit also asks for a comment when an issue is edited.

        Parameters:
        - issue: a DitIssue filled with data to save
        - comment: (optional) comment to add to the issue's event log
        """
        if issue.identifier in (None, ""):
            raise DitError("Issue has no identifier")

        self._add_issue_log_entry(issue, 'edited', comment)

        yaml_issue = IssueYamlObject.from_dit_issue(issue)
        self.issuemodel.write_issue_yaml(yaml_issue)

    def add_comment(self, dit_id, comment):
        """
        Write a new comment to a Dit item

        Parameters:
        - dit_id: Dit hash or name identifier of an issue to close
        - comment: (optional) comment text, no formatting, to add to the closed issue
        """
        if dit_id in (None, ""):
            raise DitError("Invalid dit issue identifier")
        if comment in (None, ""):
            raise DitError("Missing comment")

        dit_issue = self._get_issue_by_id(dit_id)
        self._add_issue_log_entry(dit_issue, 'commented', comment)

        yaml_issue = IssueYamlObject.from_dit_issue(dit_issue)
        self.issuemodel.write_issue_yaml(yaml_issue)

    def add_reference(self, dit_id, reference, comment=""):
        """
        Add a new reference to a Dit item

        Parameters:
        - dit_id: Dit hash or name identifier of an issue
        - reference: reference to add to the issue
        - comment: comment text, if any comment should be added
        """
        if dit_id in (None, ""):
            raise DitError("Invalid dit issue identifier")
        if reference in (None, ""):
            raise DitError("Invalid reference")

        dit_issue = self._get_issue_by_id(dit_id)
        dit_issue.references.append(reference)
        self._add_issue_log_entry(dit_issue, 'added reference', comment)

        yaml_issue = IssueYamlObject.from_dit_issue(dit_issue)
        self.issuemodel.write_issue_yaml(yaml_issue)

    def _disposition_to_str(self, disposition):
        """
        Convert disposition numerical (index) value to string

        Parameters:
        - disposition: disposition (numeric index)

        Returns:
        - disposition as string
        """
        dispositions = self.config.get_app_configs().issue_dispositions
        if disposition < 0 or disposition > len(dispositions) - 1:
            raise ApplicationError("Invalid disposition value")

        return dispositions[disposition]

    def close_issue(self, dit_id, disposition, comment=""):
        """
        Close an existing Dit item

        Parameters:
        - dit_id: Dit hash or name identifier of an issue to close
        - disposition: index of disposition, for example 0) fixed, 1) won't fix, 2) reorganized
        - comment: (optional) comment text, no formatting, to add to the closed issue
        """
        if dit_id in (None, ""):
            raise ApplicationError("Invalid dit item identifier")

        issue = self._get_issue_by_id(dit_id)
        if issue:
            issue.status = 'closed'
            if isinstance(disposition, int):
                issue.disposition = self._disposition_to_str(disposition)
            else:
                issue.disposition = disposition
            action = "closed with disposition {}".format(issue.disposition)
            self._add_issue_log_entry(issue, action, comment)

            yaml_issue = IssueYamlObject.from_dit_issue(issue)
            self.issuemodel.write_issue_yaml(yaml_issue)

    def drop_issue(self, identifier):
        """
        Remove an existing Dit issue.

        The data is lost forever when an issue is dropped.

        Parameters:
        - identifier: Dit hash or name identifier of an issue to drop

        Raises:
        - DitError if running Dit command fails
        """
        if identifier in (None, ""):
            return
        if len(identifier) != 40:
            # issue name given instead?
            issue = self._get_issue_by_id(identifier)
            if issue:
                identifier = issue.identifier
            if identifier and len(identifier) != 40:
                return
        try:
            self.issuemodel.remove_issue_yaml(identifier)
            self.item_cache.remove_issue(identifier)
        except DitError as e:
            e.error_message = "Dropping issue failed"
            raise

    def assign_issue(self, dit_id, release, comment=''):
        """
        Assign a Dit issue to a release

        Parameters:
        - dit_id: Dit hash or name identifier of an issue
        - release: name of the release to which to assign the issue
        - comment: (optional) comment text, no formatting, to add to the issue

        Raises:
        - DitError if running Dit command fails
        """
        dit_issue = self._get_issue_by_id(dit_id)
        old_release = dit_issue.release
        dit_issue.release = release
        if old_release in (None, ""):
            old_release = constants.releases.UNASSIGNED

        action = "assigned to release {} from {}".format(release, old_release)
        self._add_issue_log_entry(dit_issue, action, comment)

        yaml_issue = IssueYamlObject.from_dit_issue(dit_issue)
        self.issuemodel.write_issue_yaml(yaml_issue)

    def start_work(self, dit_id, comment=''):
        """
        Start working on an Dit issue

        Parameters:
        - dit_id: Dit hash or name identifier of an issue
        - comment: (optional) comment text, no formatting, to add to the issue

        Raises:
        - DitError if running Dit command fails
        """
        self._change_issue_status(dit_id, 'in progress', comment)

    def stop_work(self, dit_id, comment=''):
        """
        Stop working on an Dit issue

        Parameters:
        - dit_id: Dit hash or name identifier of an issue
        - comment: (optional) comment text, no formatting, to add to the issue
        """
        self._change_issue_status(dit_id, 'paused', comment)

    def _change_issue_status(self, dit_id, status, comment=''):
        """
        Change Dit issue status.

        Parameters:
        - dit_id: Dit hash or name identifier of an issue
        - status: new status to set for the issue
        - comment: (optional) comment text, no formatting, to add to the issue

        Raises:
        - DitError if running Dit command fails
        """
        if dit_id in (None, ""):
            return
        if status in (None, ""):
            return

        dit_issue = self._get_issue_by_id(dit_id)
        old_status = dit_issue.status
        dit_issue.status = status
        dit_issue.disposition = None
        action = "status changed from {} to {}".format(old_status, status)
        self._add_issue_log_entry(dit_issue, action, comment)

        yaml_issue = IssueYamlObject.from_dit_issue(dit_issue)
        self.issuemodel.write_issue_yaml(yaml_issue)

    def _get_issue_by_id(self, dit_id):
        """
        Get DitIssue from cache or file.

        Parameters:
        - dit_id: issue hash identifier or name
        """
        if dit_id in (None, ""):
            raise ApplicationError("Invalid dit item identifier")

        dit_issue = self.get_issue_from_cache(dit_id)
        if not dit_issue and len(dit_id) == 40:
            # try to load issue in case it exists, but is not cached
            dit_issue = self.get_issue_content(dit_id)
            if not dit_issue:
                raise ApplicationError('Unable to find issue: {}'.format(dit_id))
            self.reload_cache()

            # use the cached issue to keep cache up to date
            dit_issue = self.get_issue_from_cache(dit_id)
            if not dit_issue:
                raise ApplicationError('Unable to find issue even after reload: {}'.format(dit_id))

        return dit_issue

    def _add_issue_log_entry(self, issue, action, comment=None):
        """
        Add a new log entry to an issue

        Parameters:
        - issue: issue to which to add the change
        - action: title describing what was done
        - comment: (optional) a comment to the log, empty by default
        """
        creator = self.config.get_default_creator()
        issue.add_log_entry(None, action, creator, comment)
