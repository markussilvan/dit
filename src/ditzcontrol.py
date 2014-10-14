#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker
"""

import subprocess


class ApplicationError(Exception):
    """
    A common exception type to use in an application
    """
    def __init__(self, error_message):
        """
        Initilize a new exception

        Parameters:
        - error_message: a description of the error
        """
        super(Exception, self).__init__()
        self.error_message = error_message


class DitzError(ApplicationError):
    """
    A specific error type for errors originating from Ditz command line tool
    """
    def __init__(self, error_message):
        """
        Initilize a new exception

        Parameters:
        - error_message: a description of the error
        """
        super(Exception, self).__init__(error_message)


class DitzItem():
    """
    A Ditz item which can be an issue or an release.
    Can contain all data of that particular item or
    just the type and a header.
    A status is also commonly set for issues.
    """
    def __init__(self, item_type, title, name=None, issue_type=None, status=None,
            description=None, creator=None, age=None, release=None,
            references=None, identifier=None, log=None):
        """
        Initialize new DitzItem.
        At least type and title must be set for releases.
        For issues, also status should be set.
        """
        self.item_type = item_type
        self.name = name

        self.title = title
        self.issue_type = issue_type
        self.status = status
        self.description = description
        self.creator = creator
        self.age = age
        self.release = release
        self.references = references
        self.identifier = identifier
        self.log = log

    def __str__(self):
        """
        Serialize to string. Mimic output of Ditz command line.
        """
        return "Issue {}\n{}".format(self.name, len(self.name) * '-') + '\n' + \
            "Title: {}".format(self.title) + '\n' + \
            "Description:\n{}".format(self.description) + '\n' + \
            "Type: {}".format(self.issue_type) + '\n' + \
            "Status: {}".format(self.status) + '\n' + \
            "Creator: {}".format(self.creator) + '\n' + \
            "Age: {}".format(self.age) + '\n' + \
            "Release: {}".format(self.release) + '\n' + \
            "References:\n{}".format(self.references) + \
            "Identifier: {}".format(self.identifier) + '\n' + \
            "Event log:\n{}".format(self.log)

class DitzControl():
    """
    This class handles communication to Ditz command line interface.
    Ditz issue data is read using the Ditz command line tool.
    """
    def __init__(self):
        self.ditz_cmd = "ditz"
        self.ditz_items = []

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

    def get_items(self):
        """
        Get a list of all tasks, features and bugs listed in Ditz.

        Returns:
        - A list of DitzItems
        """
        del self.ditz_items[:]
        items = self._run_command("todo")
        for i, item in enumerate(items):
            item_text = item.replace('\n', '')

            item_data = item_text.split(':', 1)
            if len(item_data[0]) == 0:
                # empty line, skip
                continue
            name_and_status = item_data[0]
            status = self._status_identifier_to_string(name_and_status[:1])
            if status != None:
                # an issue
                title = item_data[1].strip()
                name = name_and_status[1:].strip() # drop status from the beginning
                self.ditz_items.append(DitzItem('issue', title, name, None, status))
            else:
                # a release
                name = None
                title = name_and_status.split('(', 1)[0].rstrip() # just take the version
                if item_data[0] != "Unassigned":
                    name = "Release"
                self.ditz_items.append(DitzItem('release', title, name))

        return self.ditz_items

    def get_item_status_by_ditz_id(self, ditz_id):
        """
        Get status of an Ditz issue loaded in the cached list of issues.

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue

        Returns:
        - issue status
        - None if requested issue is not found
        """
        for item in self.ditz_items:
            if item.name == ditz_id:
                return item.status
        return None

    def get_item_type_by_ditz_id(self, ditz_id):
        """
        Get status of an Ditz issue loaded in the list of issues.

        Parameters:
        - ditz_id: Ditz name of an issue

        Returns:
        - issue type
        - None if requested issue is not found
        """
        for item in self.ditz_items:
            if item.name == ditz_id:
                return item.item_type
        return None

    def get_item_content(self, ditz_id):
        """
        Get all content of one item by it's ditz id hash.

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
        #TODO: check if ditz returned error
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
        if status not in ['unstarted', 'in progress', 'paused']: #TODO: make a function (also check UI options)
            raise DitzError("Error parsing issue status from Ditz output data, unrecognized value")

        creator = self._parse_ditz_item_variable(ditz_data, "Creator")
        age = self._parse_ditz_item_variable(ditz_data, "Age")
        release = self._parse_ditz_item_variable(ditz_data, "Release")

        # references and identifier in one go
        references_line = ditz_data.next().lstrip()
        references = ""
        identifier_line = ""
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
            stripped_line = line.strip() #TODO: clean this up, model after description part?
            if len(stripped_line) > 0:
                if len(log) > 0:
                    log = "{}\n{}".format(log, stripped_line)
                else:
                    log = stripped_line
            else:
                break

        ditz_item = DitzItem("issue", title, name, issue_type, status, description, creator, age,
                release, references, identifier, log)
        #TODO: use existing item in cache instead? (that would cache all this data too)
        #      or replace the item with this new item
        return ditz_item

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
            self._run_interactive_command("comment " + ditz_id, comment, "/stop")
        except DitzError,e:
            e.error_message = "Adding a comment on Ditz failed"
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
            return
        if disposition < 1 or disposition > 3:
            return
        try:
            self._run_interactive_command("close " + ditz_id, disposition, comment, "/stop")
        except DitzError,e:
            e.error_message = "Closing an issue on Ditz failed"
            raise

    def drop_issue(self, ditz_id):
        """
        Remove an existing Ditz item

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue to drop

        Raises:
        - DitzError if running Ditz command fails
        """
        if ditz_id == None or ditz_id == "":
            return
        try:
            self._run_command("drop " + ditz_id)
        except DitzError,e:
            e.error_message = "Dropping issue failed"
            raise

    def start_work(self, ditz_id, comment):
        """
        Start working on an Ditz item

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
        except DitzError,e:
            e.error_message = "Starting work on a Ditz issue failed"
            raise

    def stop_work(self, ditz_id, comment):
        """
        Stop working on an Ditz item

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue
        - comment: (optional) comment text, no formatting, to add to the issue
        """
        if ditz_id == None or ditz_id == "":
            return
        try:
            self._run_interactive_command("stop " + ditz_id, comment, "/stop")
        except DitzError,e:
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
        except DitzError,e:
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
        cmd = "{0} {1}".format(self.ditz_cmd, cmd)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
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
        cmd = [self.ditz_cmd]
        for parameter in cmdline.split(' '):
            cmd.append(parameter)
        p = subprocess.Popen(cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        for argument in args:
            p.stdin.write(str(argument) + "\n")
        retval = p.wait()
        if retval != 0:
            raise DitzError("Ditz returned an error")
        return p.stdout.readlines()

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
        issue_types = {
            'bugfix' : 1,
            'feature' : 2,
            'task' : 3
        }
        if issue_type in issue_types:
            return issue_types[issue_type]
        return None

    def _parse_ditz_item_variable(self, ditz_data, variable_name, input_line=None):
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


