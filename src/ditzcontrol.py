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
        #FIXME: this is a total hack, just to be used during refactoring.
        issue = self.get_issue_content_from_ditz(issue_name)
        if issue:
            return issue.identifier
        return None

    def get_issue_content(self, identifier, update_cache=True):
        """
        Get all content of one issue by its identifier hash.

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
            identifier = self.get_issue_identifier(identifier)
            if identifier and len(identifier) != 40:
                return None
        yaml_issue = self.issuecontrol.read_issue_yaml(identifier)
        ditz_item = yaml_issue.toDitzItem()
        if update_cache:
            self.item_cache.add_issue(ditz_item)
            #self.item_cache.sort_issues(rename = True)
        return ditz_item

    def get_issue_content_from_ditz(self, ditz_id):
        """
        Get all content of one item by its ditz id hash.

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue

        Returns:
        - A Ditz item object filled with information of that issue
        - None if ditz_id is invalid
        """
        if ditz_id == None or ditz_id == "":
            return None
        try:
            ditz_data = iter(self._run_command("show " + ditz_id))
        except DitzError:
            return None
        name = ditz_data.next().split()[1].strip()

        ditz_data.next() # skip line 1, it's just a line (no pun intended)

        title = self._parse_ditz_item_variable(ditz_data, "Title")

        description_line = ditz_data.next()
        if description_line == "Description: \n":
            # multi-line description
            description = ""
            for line in ditz_data:
                if len(line) > 2:
                    description = "{}{}".format(description, line[2:])
                else:
                    break
        elif description_line[:12] == "Description:":
            # one line description
            description = self._parse_ditz_item_variable(ditz_data, "Description", description_line)
        else:
            raise DitzError("Error parsing issue description from Ditz output")

        issue_type = self._parse_ditz_item_variable(ditz_data, "Type")
        if self._issue_type_string_to_id(issue_type) == None:
            raise DitzError("Error parsing issue type from Ditz output data, unrecognized value")

        status = self._parse_ditz_item_variable(ditz_data, "Status")
        if not self._is_valid_issue_status(status):
            raise DitzError("Error parsing issue status from Ditz output data, unrecognized value")

        creator = self._parse_ditz_item_variable(ditz_data, "Creator")
        age = self._parse_ditz_item_variable(ditz_data, "Age")
        release = self._parse_ditz_item_variable(ditz_data, "Release")

        # references and identifier in one go
        references_line = ditz_data.next().lstrip()
        references = ""
        if references_line != "References: \n":
            raise DitzError("Error parsing issue references from Ditz output")
        for line in ditz_data:
            if line.lstrip().split(' ', 1)[0] != "Identifier:":
                references = "{}{}".format(references, line[2:])
            else:
                identifier = self._parse_ditz_item_variable(ditz_data, "Identifier", line)
                break


        # skip one empty line before event log starts
        if ditz_data.next().strip() != "":
            raise DitzError("Error parsing event log from Ditz output data")

        if ditz_data.next().strip() != "Event log:":
            raise DitzError("Error parsing event log from Ditz output data")

        log = ""
        for line in ditz_data:
            stripped_line = line.strip()
            if len(stripped_line) > 0:
                if len(log) > 0:
                    log = "{}\n{}".format(log, stripped_line)
                else:
                    log = stripped_line
            else:
                break

        ditz_item = DitzItem("issue", title, name, issue_type, None, status, None,
                description, creator, age, release, references, identifier, log)
        #TODO: use existing item in cache instead? (that would cache all this data too)
        #      or replace the item with this new item
        return ditz_item

    def add_issue(self, issue):
        """
        Add new issue to Ditz
        Ditz also asks for a comment when an issue is added,
        but saving a comment is not supported.

        Parameters:
        - a DitzItem filled with data to save
        """
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

    def edit_issue(self, issue):
        """
        Modify an existing Ditz issue.
        Ditz also asks for a comment when an issue is edited,
        but saving a comment is not supported.

        Parameters:
        - a DitzItem filled with data to save
        """
        if issue.identifier == None or issue.identifier == "":
            raise DitzError("Issue has no identifier")
        yaml_issue = IssueYamlObject.fromDitzItem(issue)
        self.issuecontrol.write_issue_yaml(yaml_issue)

    def add_comment(self, ditz_id, comment):
        """
        Write a new comment to a Ditz item

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue
        - comment: comment text, no formatting
        """
        if ditz_id == None or ditz_id == "":
            return
        try:
            self._run_interactive_command("comment {}".format(ditz_id), comment, "/stop")
        except DitzError, e:
            e.error_message = "Adding a comment on Ditz failed"
            raise

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
        try:
            self._run_interactive_command("close {}".format(ditz_id), disposition, comment, "/stop")
        except DitzError, e:
            e.error_message = "Closing an issue on Ditz failed"
            raise

    def drop_issue(self, ditz_id):
        """
        Remove an existing Ditz issue

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue to drop

        Raises:
        - DitzError if running Ditz command fails
        """
        if ditz_id == None or ditz_id == "":
            return
        try:
            self._run_command("drop " + ditz_id)
        except DitzError, e:
            e.error_message = "Dropping issue failed"
            raise

    def assign_issue(self, ditz_id, release, comment):
        """
        Assign a Ditz issue to a release

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue
        - release: which release to assign the issue
        - comment: (optional) comment text, no formatting, to add to the issue

        Raises:
        - DitzError if running Ditz command fails
        """
        ditz_issue = self.get_issue_from_cache(ditz_id)
        if not ditz_issue:
            # try to load issue in case it exists, but is not cached
            ditz_issue = self.get_issue_content(ditz_id)
        ditz_issue.release = release
        if comment and comment != "":
            #TODO: implementation to add a comment if given
            pass
        yaml_issue = IssueYamlObject.fromDitzItem(ditz_issue)
        self.issuecontrol.write_issue_yaml(yaml_issue)

    def start_work(self, ditz_id, comment):
        """
        Start working on an Ditz issue

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue
        - comment: (optional) comment text, no formatting, to add to the issue

        Raises:
        - DitzError if running Ditz command fails
        """
        if ditz_id == None or ditz_id == "":
            return
        try:
            self._run_interactive_command("start " + ditz_id, comment, "/stop")
        except DitzError, e:
            e.error_message = "Starting work on a Ditz issue failed"
            raise

    def stop_work(self, ditz_id, comment):
        """
        Stop working on an Ditz issue

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue
        - comment: (optional) comment text, no formatting, to add to the issue
        """
        if ditz_id == None or ditz_id == "":
            return
        try:
            self._run_interactive_command("stop " + ditz_id, comment, "/stop")
        except DitzError, e:
            e.error_message = "Stopping work on a Ditz issue failed"
            raise

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


