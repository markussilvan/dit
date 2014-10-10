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


class DitzControl():
    """
    This class handles communication to Ditz command line interface.
    Ditz issue data is read using the Ditz command line tool.
    """
    def __init__(self):
        self.ditz_cmd = "ditz"

    def run_command(self, cmd):
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
            raise ApplicationError("Ditz returned an error")
        return p.stdout.readlines()

    def run_interactive_command(self, cmdline, *args):
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
            #p.stdin.write("/stop\n")
        retval = p.wait()
        if retval != 0:
            raise ApplicationError("Ditz returned an error")
        return p.stdout.readlines()

    def get_releases(self):
        """
        TODO

        Returns:
        - list of release names
        """
        releases = self.run_command("releases")
        return releases

    def get_items(self):
        """
        Get a list of all tasks, features and bugs listed in Ditz.

        Returns:
        - A list of id's and topics of all items
        """
        items = self.run_command("todo")
        for i, item in enumerate(items):
                items[i] = item.replace('\n', '')
        #TODO: parse the output and return it in a sensible format
        # the first character of the line can be used to recognize
        # if the line contains a name of a release or an issue
        return items

    def get_item(self, ditz_id):
        """
        Get all content of one item by it's ditz id hash.

        Parameters:
        - ditz_id: Ditz identifier hash of an issue

        Returns:
        - A Ditz item object filled with information of that issue
        - None if ditz_id is invalid
        """
        if ditz_id == None or ditz_id == "":
            return None
        try:
            item = self.run_command("show " + ditz_id)
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
        - ditz_id: Ditz identifier hash of an issue
        - comment: comment text, no formatting
        """
        if ditz_id == None or ditz_id == "":
            return
        try:
            item = self.run_interactive_command("comment " + ditz_id, comment, "/stop")
        except ApplicationError:
            #TODO: reraise or return something, so an error can be shown to user?
            return

    def close_issue(self, ditz_id, disposition, comment=""):
        """
        Close an existing Ditz item

        Parameters:
        - ditz_id: Ditz identifier hash of an issue to close
        - disposition: 1) fixed, 2) won't fix, 3) reorganized
        - comment: (optional) comment text, no formatting, to add to the closed issue
        """
        if ditz_id == None or ditz_id == "":
            return
        if disposition < 1 or disposition > 3:
            return
        try:
            item = self.run_interactive_command("close " + ditz_id, disposition, comment, "/stop")
        except ApplicationError:
            #TODO: reraise or return something, so an error can be shown to user?
            return


