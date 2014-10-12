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
    Doesn't contain all data of that particular item,
    just the type and a header.
    A status can also be set for issues.
    """
    def __init__(self, item_type, item_header, item_name=None, status=None):
        self.item_type = item_type
        self.item_header = item_header
        self.item_name = item_name
        self.item_status = status


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
                item_header = item_data[1].strip()
                item_name = name_and_status[1:].strip() # drop status from the beginning
                self.ditz_items.append(DitzItem('issue', item_header, item_name, status))
            else:
                # a release
                item_name = None
                item_header = name_and_status.split('(', 1)[0].rstrip() # just take the version
                if item_data[0] != "Unassigned":
                    item_name = "Release"
                self.ditz_items.append(DitzItem('release', item_header, item_name))

        return self.ditz_items

    def get_item_status_by_ditz_id(self, ditz_id):
        """
        Get status of an Ditz issue loaded in the list of issues.

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue

        Returns:
        - issue status
        - None if issue not found
        """
        for item in self.ditz_items:
            if item.item_name == ditz_id:
                return item.item_status
        return None

    def get_item_type_by_ditz_id(self, ditz_id):
        """
        Get status of an Ditz issue loaded in the list of issues.

        Parameters:
        - ditz_id: Ditz name of an issue

        Returns:
        - issue type
        - None if issue not found
        """
        for item in self.ditz_items:
            if item.item_name == ditz_id:
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
            item = self._run_command("show " + ditz_id)
        except ApplicationError:
            return None
        serialized_item = ""
        for line in item:
            serialized_item += line.lstrip()
        #TODO: format output more nicely? or structure output in a list?
        return serialized_item

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

    def drop_issue(self, ditz_id, comment=""):
        """
        Remove an existing Ditz item

        Parameters:
        - ditz_id: Ditz hash or name identifier of an issue to drop
        - disposition: 1) fixed, 2) won't fix, 3) reorganized
        - comment: (optional) comment text, no formatting, to add to the dropped issue

        Raises:
        - DitzError if running Ditz command fails
        """
        if ditz_id == None or ditz_id == "":
            return
        try:
            self._run_interactive_command("drop " + ditz_id, comment, "/stop")
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
            '_': "new",
            '>': "started",
            '=': "paused"
        }
        if status_id in states:
            return states[status_id]
        return None

