#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker

A settings dialog box
"""

from PyQt4 import QtGui, uic

from config import ConfigControl

class SettingsDialog(QtGui.QDialog):
    """
    A settings dialog with multiple inputs and Cancel/Ok buttons.
    """
    def __init__(self, config):
        """
        Initialize user interface for the dialog

        Parameters:
        - config: ConfigControl to access settings data
        """
        super(SettingsDialog, self).__init__()

        self.config = config
        self.config.read_config_file() # reload, just in case
        self.ditz_settings_changed = False

        uic.loadUi('../ui/settings_dialog.ui', self)

        self.lineEditName.editingFinished.connect(self.ditz_settings_edited)
        self.lineEditEmail.editingFinished.connect(self.ditz_settings_edited)
        self.lineEditIssueDir.editingFinished.connect(self.ditz_settings_edited)

        self.lineEditName.setText(self.config.settings.name)
        self.lineEditEmail.setText(self.config.settings.email)
        self.lineEditIssueDir.setText(self.config.settings.issue_dir)

    def ditz_settings_edited(self):
        """
        Set ditz_settings_changed flag, so we know settings should be written
        to the file if dialog is accepted
        """
        self.ditz_settings_changed = True

    def accept(self):
        """
        Ok is pressed on the GUI
        Save settings
        """
        if self.ditz_settings_changed == True:
            self.config.settings.name = str(self.lineEditName.text())
            self.config.settings.email = str(self.lineEditEmail.text())
            self.config.settings.issue_dir = str(self.lineEditIssueDir.text())
            self.config.write_config_file()
            self.ditz_settings_changed = False
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
        """
        self.exec_()


