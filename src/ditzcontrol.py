#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker
"""

import subprocess


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
        for line in p.stdout.readlines():
            print line,
        retval = p.wait()
        #TODO: return the command output
        #TODO: raise an exception if the command returns an error

    def get_items(self):
        """
        Get a list of all tasks, features and bugs listed in Ditz.

        Returns:
        - A list of id's and topics of all items
        """
        self.run_command("todo")
        #TODO: parse the output and return it in a sensible format

    def get_item(self, ditz_id):
        """
        Get all content of one item by it's ditz id hash.

        Parameters:
        - ditz_id: Ditz identifier hash of an issue

        Returns:
        - A Ditz item object filled with information of that issue
        """
        self.run_command("show " + ditz_id)
        #TODO: parse output

