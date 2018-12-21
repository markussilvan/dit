#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dit GUI

A GUI frontend for Dit issue tracker

A settings dialog box
"""

import os

from PyQt5 import QtWidgets, uic

from config import ConfigControl
from common.errors import ApplicationError

class SettingsDialog(QtWidgets.QDialog):
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

        if not isinstance(config, ConfigControl):
            raise ApplicationError('Invalid config parameter')

        self.config = config
        try:
            self.config.load_configs() # reload, just in case
        except ApplicationError:
            pass

        self.dit_settings_changed = False
        self.app_settings_changed = False

        my_path = os.path.dirname(os.path.realpath(__file__))
        uic.loadUi(my_path + '/../ui/settings_dialog.ui', self)

        self._init_dit_settings_tab()
        self._init_ui_settings_tab()

    def _init_dit_settings_tab(self):
        """
        Initialize Dit settings tab with current values
        """
        settings = self.config.get_dit_configs()
        self.lineEditName.editingFinished.connect(self.dit_settings_edited)
        self.lineEditEmail.editingFinished.connect(self.dit_settings_edited)
        self.lineEditIssueDir.editingFinished.connect(self.dit_settings_edited)

        self.lineEditName.setText(settings.name)
        self.lineEditEmail.setText(settings.email)
        self.lineEditIssueDir.setText(settings.issue_dir)

    def _init_ui_settings_tab(self):
        """
        Initialize UI settings tab with current values
        """
        settings = self.config.get_app_configs()

        self.checkBoxRememberWindowSize.toggled.connect(self.app_settings_edited)
        self.comboBoxIssueType.currentIndexChanged.connect(self.app_settings_edited)

        self.checkBoxRememberWindowSize.setChecked(settings.remember_window_size)
        for issue_type in settings.issue_types:
            self.comboBoxIssueType.addItem(issue_type)

        default_issue_type = settings.default_issue_type
        index = self.comboBoxIssueType.findText(default_issue_type)
        if index >= 0:
            self.comboBoxIssueType.setCurrentIndex(index)

    def dit_settings_edited(self):
        """
        Set dit_settings_changed flag, so we know settings should be written
        to the file if dialog is accepted
        """
        self.dit_settings_changed = True

    def app_settings_edited(self):
        """
        Set application settings changed flag, so we know app settings should
        be written to a file if dialog is accepted
        """
        self.app_settings_changed = True

    def accept(self):
        """
        Ok is pressed on the GUI
        Save settings
        """
        dit_settings = self.config.get_dit_configs()
        app_settings = self.config.get_app_configs()
        if self.dit_settings_changed is True:
            dit_settings.name = str(self.lineEditName.text())
            dit_settings.email = str(self.lineEditEmail.text())
            dit_settings.issue_dir = str(self.lineEditIssueDir.text())
            if self.config.ditconfig.write_config_file() is True:
                self.dit_settings_changed = False
            else:
                raise ApplicationError("Error saving dit configuration file")

        if self.app_settings_changed is True:
            app_settings.default_issue_type = str(self.comboBoxIssueType.currentText())
            app_settings.remember_window_size = bool(self.checkBoxRememberWindowSize.isChecked())
            if self.config.appconfig.write_config_file() is True:
                self.app_settings_changed = False
            else:
                raise ApplicationError("Error saving application configuration file")

        super(SettingsDialog, self).accept()

    def reject(self):
        """
        Cancel is clicked on the GUI
        """
        super(SettingsDialog, self).reject()

    def show_settings(self):
        """
        Show the dialog and get a settings from the user
        If Dit id and settings are given, save the comment to Dit
        """
        self.exec_()
