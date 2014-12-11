#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker
"""

import subprocess

from itemcache import ItemCache
from common.items import DitzItem
from common.errors import ApplicationError, DitzError
from common.utils.nonblockingstreamreader import NonBlockingStreamReader
from yamlcontrol import IssueYamlControl, IssueYamlObject
from config import ConfigControl


class DitzControl():
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

    def get_valid_issue_states(self):
        """
        Get a list of valid states for a Ditz issue

        Returns:
        - list of states
        """
        return ["unstarted", "in progress", "paused"]

    def get_valid_issue_types(self):
        """
        Get a list of valid issue types for a Ditz issue

        Returns:
        - list of issue types
        """
        return ["bugfix", "feature", "task"]

    def get_valid_issue_dispositions(self):
        """
        Get a list of valid issue dispositions for a Ditz issue

        Returns:
        - list of issue dispositions
        """
        return ["fixed", "won't fix", "reorganized"]

    def get_releases(self):
        """
        Get a list of release names from Ditz

        Returns:
        - list of release names
        """
        releases = []
        release_data = self._run_command("releases")
        for line in release_data:
            releases.append(line.split()[0])
        return releases

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
            self.item_cache.add_release(DitzItem('release', title, 'Release'))
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
            issues = self.item_cache.sort_issues_by_status(issues) #TODO: move this function to DitzControl or utils?
            items.extend(issues)

        # add unassigned items
        items.append(DitzItem('release', 'Unassigned'))
        issues = self.item_cache.get_issues_by_release(None)
        issues = self.item_cache.sort_issues_by_status(issues)
        items.extend(issues)

        return items

    def get_issue_status_by_ditz_id(self, ditz_id): #TODO: move this function to ItemCache
        """
        Get status of an Ditz issue loaded in the cached list of issues.

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue

        Returns:
        - issue status
        - None if requested issue is not found
        """
        for item in self.item_cache.issues:
            if item.name == ditz_id:
                return item.status
        return None

    def get_issue_from_cache(self, ditz_id):
        """
        Get DitzItem from cache by Ditz identifier or name.

        Parameters:
        - ditz_id: Ditz name or identifier of an issue

        Returns:
        - DitzItem object
        - None if requested item is not found
        """
        issue = self.item_cache.get_issue(ditz_id)
        return issue

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
        ditz_item = yaml_issue.toDitzItem()
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
        - issue: a DitzItem filled with data to save
        - comment: (optional) comment to add to the issue's event log
        """
        #TODO: comment not used
        # run the commands
        output = ""
        try:
            if issue.release not in [None, "", "Unassigned"]:
                # first figure out right selection for release
                release_selection = str(self.get_releases().index(issue.release) + 1)
                output = self._run_interactive_command("add", issue.title, issue.description, "/stop",
                        issue.issue_type[:1], 'y', release_selection, issue.creator, "/stop")
            else:
                # example: title, description, t, n, creator, /stop
                output = self._run_interactive_command("add", issue.title, issue.description, "/stop",
                        issue.issue_type[:1], 'n', issue.creator, "/stop")
        except DitzError, e:
            e.error_message = "Adding a new issue to Ditz failed"
            raise

        # first get identifier for the new issue from Ditz output
        if output[-6:] == ".yaml\n":
            identifier = output[-46:-6]
        else:
            raise DitzError("Parsing ditz add output failed")

        # change issue status if needed
        if issue.status != "unstarted":
            try:
                self.start_work(identifier, "")
                if issue.status == "paused":
                    self.stop_work(identifier, "")
            except DitzError, e:
                e.error_message = "Setting issue state failed"
                raise

        # add a reference if given (input of only one reference supported)
        if issue.references != None and issue.references != "":
            try:
                self.add_reference(identifier, issue.references)
            except DitzError, e:
                e.error_message = "Adding reference to issue failed"
                raise

    def edit_issue(self, issue, comment=''):
        """
        Modify an existing Ditz issue.
        Ditz also asks for a comment when an issue is edited,
        but saving a comment is not supported.

        Parameters:
        - issue: a DitzItem filled with data to save
        - comment: (optional) comment to add to the issue's event log
        """
        if issue.identifier == None or issue.identifier == "":
            raise DitzError("Issue has no identifier")

        self._add_issue_log_entry(issue, 'edited', comment)

        yaml_issue = IssueYamlObject.fromDitzItem(issue)
        self.issuecontrol.write_issue_yaml(yaml_issue)

    def add_comment(self, ditz_id, comment):
        """
        Write a new comment to a Ditz item

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue to close
        - comment: (optional) comment text, no formatting, to add to the closed issue
        """
        if ditz_id == None or ditz_id == "":
            raise ApplicationError("Invalid ditz issue identifier")
        if comment == None or comment == "":
            raise ApplicationError("Missing comment")

        ditz_issue = self._get_issue_by_id(ditz_id)
        self._add_issue_log_entry(ditz_issue, 'commented', comment)

        yaml_issue = IssueYamlObject.fromDitzItem(ditz_issue)
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
            return
        try:
            self._run_interactive_command("add-reference {}".format(ditz_id),
                    reference, comment, "/stop")
        except DitzError, e:
            e.error_message = "Adding a reference on Ditz failed"
            raise

    def _disposition_to_str(self, disposition):
        """
        Convert disposition numerical (index) value to string

        Parameters:
        - disposition: disposition (numeric)

        Returns:
        - disposition as string
        """
        dispositions = self.get_valid_issue_dispositions()
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

        yaml_issue = IssueYamlObject.fromDitzItem(ditz_issue)
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

        yaml_issue = IssueYamlObject.fromDitzItem(ditz_issue)
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
        try:
            self._run_interactive_command("release " + release_name, comment, "/stop")
        except DitzError, e:
            e.error_message = "Making release on Ditz failed"
            raise

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

        yaml_issue = IssueYamlObject.fromDitzItem(ditz_issue)
        self.issuecontrol.write_issue_yaml(yaml_issue)

    def _run_command(self, cmd):
        """
        Run a Ditz command on the command line tool

        Parameters:
        - cmd: the Ditz command and its parameters

        Returns:
        - output of the command as string
        """
        cmd = [self.ditz_cmd] + cmd.split()
        try:
            p = subprocess.Popen(cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
            retval = p.wait()
        except OSError:
            raise DitzError("Error running Ditz")
        if retval != 0:
            raise DitzError("Ditz returned an error")
        return p.stdout.readlines()

    def _run_interactive_command(self, cmdline, *args):
        """
        Run a Ditz command on the command line tool
        Other arguments are given to the command one by one, when
        Ditz prompts for more input

        Parameters:
        - cmdline: the Ditz command and its parameters in a list
        - args: (optional) arguments to give to the command, one by one

        Returns:
        - output of the command as string
        """
        cmd = [self.ditz_cmd] + cmdline.split()

        p = subprocess.Popen(cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, shell=False)

        reader = NonBlockingStreamReader(p.stdout)

        # read output and issue commands
        output = ""
        for argument in args:
            # read Ditz output
            output = output + self._read_all_input(reader)
            # send arguments
            p.stdin.write(str(argument) + "\n")

        # read last of the output
        output = output + self._read_all_input(reader)
        return output

    def _read_all_input(self, reader, timeout=0.5):
        """
        Read all input from given stream until
        no new character have arrived during
        given timeout.

        Parameters:
        - stream: stream to read

        Returns:
        - lines read from stream
        """
        output = ""
        while True:
            try:
                line = reader.read(timeout)
            except Exception:
                break
            if not line:
                break
            output = output + line
        return output

    def _status_identifier_to_string(self, status_id):
        """
        Convert a status identifier character from Ditz text output
        to string representation.

        Parameters:
        - status_id: status character

        Returns:
        - status string
        - None on invalid input
        """
        states = {
            '_': "unstarted",
            '>': "in progress",
            '=': "paused"
        }
        if status_id in states:
            return states[status_id]
        return None

    def _issue_type_string_to_id(self, issue_type):
        """
        Convert issue type, as string, to a number representation

        Parameters:
        - issue_type: issue type as string

        Returns:
        - a number value, an index that represents that same issue type
        - None, if given issue type is not recognized
        """
        issue_types = {
            'bugfix' : 1,
            'feature' : 2,
            'task' : 3
        }
        if issue_type in issue_types:
            return issue_types[issue_type]
        return None

    def _parse_ditz_item_variable(self, ditz_data, variable_name, input_line=None):
        """
        Parse a variable value from "ditz show" command output.

        Parameters:
        - ditz_data: ditz command output,
                     starting from the line containing the variable
        - variable_name: name of the variable to parse from the output data
        - input_line: (optional) if given, use this text line instead of ditz command output

        Returns:
        - value set for the variable
        """
        if input_line == None:
            variable_line = ditz_data.next().strip().split(' ', 1)
        else:
            variable_line = input_line.strip().split(' ', 1)
        if variable_line[0][:-1] != variable_name:
            raise DitzError("Error parsing {} from Ditz output data".format(variable_name))
        if len(variable_line) > 1:
            value = variable_line[1]
        else:
            value = ""
        return value

    def _is_valid_issue_status(self, status):
        """
        Check if a given string is valid status for a Ditz issue.

        Parameters:
        - status: issue status string

        Returns:
        - True if string is a valid issue status
        - False if not
        """
        if status in ['unstarted', 'in progress', 'paused']:
            return True
        return False

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
        creator = '{} <{}>'.format(self.config.settings.name, self.config.settings.email)
        issue.add_log_entry(None, action, creator, comment)


