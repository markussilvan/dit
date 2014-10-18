#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker
"""

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
        super(ApplicationError, self).__init__()
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
        super(DitzError, self).__init__(error_message)

    def __str__(self):
        """
        Printing out the exception

        Returns:
        - exception information string
        """
        return "DitzError: {}".format(e.error_message)


