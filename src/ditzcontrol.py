#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker
"""

import subprocess


class ApplicationException(Exception):
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
        pass

    def run_command(self, cmd):
        """
        Run a Ditz command on the command line tool

        Parameters:
        - cmd: the Ditz command and its parameters

        Returns:
        - output of the command as string
        """
        cmd = "ditz " + cmd
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        if retval != 0:
            raise ApplicationException("Ditz returned an error")
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
        """
        item = self.run_command("show " + ditz_id)
        serialized_item = ""
        for line in item:
            serialized_item += line.lstrip()
        #TODO: format output more nicely? or structure output in a list?
        return serialized_item

