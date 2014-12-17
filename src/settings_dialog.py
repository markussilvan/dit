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

        if not isinstance(config, ConfigControl):
            raise ApplicationError('Invalid config parameter')

        self.config = config
        self.config.load_configs() # reload, just in case
        self.ditz_settings_changed = False
        self.app_settings_changed = False

        uic.loadUi('../ui/settings_dialog.ui', self)

        self._init_ditz_settings_tab()
        self._init_ui_settings_tab()

    def _init_ditz_settings_tab(self):
        """
        Initialize Ditz settings tab with current values
        """
        settings = self.config.get_ditz_configs()
        self.lineEditName.editingFinished.connect(self.ditz_settings_edited)
        self.lineEditEmail.editingFinished.connect(self.ditz_settings_edited)
        self.lineEditIssueDir.editingFinished.connect(self.ditz_settings_edited)

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

        for issue_type in self.config.get_valid_issue_types():
            self.comboBoxIssueType.addItem(issue_type)

        default_issue_type = settings.default_issue_type
        index = self.comboBoxIssueType.findText(default_issue_type)
        if index >= 0:
            self.comboBoxIssueType.setCurrentIndex(index)

    def ditz_settings_edited(self):
        """
        Set ditz_settings_changed flag, so we know settings should be written
        to the file if dialog is accepted
        """
        self.ditz_settings_changed = True

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
        ditz_settings = self.config.get_ditz_configs()
        app_settings = self.config.get_app_configs()
        if self.ditz_settings_changed == True:
            ditz_settings.name = str(self.lineEditName.text())
            ditz_settings.email = str(self.lineEditEmail.text())
            ditz_settings.issue_dir = str(self.lineEditIssueDir.text())
            self.config.ditzconfig.write_config_file()
            self.ditz_settings_changed = False

        if self.app_settings_changed == True:
            app_settings.default_issue_type = str(self.comboBoxIssueType.currentText())
            app_settings.remember_window_size = bool(self.checkBoxRememberWindowSize.isChecked())
            self.config.appconfig.write_config_file()
            self.app_settings_changed = False

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


