#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker

A settings dialog box
"""

import sys
from PyQt4 import QtGui, uic

from configcontrol import ConfigControl

class SettingsDialog(QtGui.QDialog):
    """
    A settings dialog with multiple inputs and Cancel/Ok buttons.
    """
    def __init__(self):
        """
        Initialize user interface for the dialog
        """
        super(SettingsDialog, self).__init__()

        self.configControl = ConfigControl()
        self.settings = None

        uic.loadUi('../ui/settings_dialog.ui', self)

    def accept(self):
        """
        Ok is pressed on the GUI
        Save settings
        """
        self.settings["name"] = str(self.lineEditName.text())
        self.settings["email"] = str(self.lineEditEmail.text())
        self.settings["issue_dir"] = str(self.lineEditIssueDir.text())
        if self.settings_changed == True:
            self.configControl.save_settings(self.settings)
        super(SettingsDialog, self).accept()

    def reject(self):
        """
        Cancel is clicked on the GUI
        """
        super(SettingsDialog, self).reject()

    def show_settings(self):
        """
        Show the dialog and get a settings from the user
        If Ditz id and settings are given, save the comment to Ditz

        Returns:
        - Settings written by the user
        """
        self.exec_()
        return self.settings


