#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker

A dialog for assigning an issue to a release
"""

from PyQt4 import QtGui, uic

from ditzcontrol import DitzControl
from common.errors import ApplicationError

class AssignDialog(QtGui.QDialog):
    """
    A dialog with couple of inputs and Cancel/Ok buttons.
    """
    def __init__(self, ditz, ditz_id=None):
        """
        Initialize user interface for the dialog

        Parameters:
        - ditz: DitzControl to access data
        - ditz_id: Ditz item to assign
        """
        super(AssignDialog, self).__init__()

        if not isinstance(ditz, DitzControl):
            raise ApplicationError("Construction failed due to invalid ditz (DitzControl) parameter")

        self.ditz = ditz
        self.ditz_id = ditz_id

        uic.loadUi('../ui/assign_dialog.ui', self)

        self.comboBoxRelease.addItem("Unassigned")
        for release in self.ditz.config.get_unreleased_releases():
            self.comboBoxRelease.addItem(release)

    def accept(self):
        """
        Ok is pressed on the GUI

        Given issue is now assigned to the selected release.
        """
        release = str(self.comboBoxRelease.currentText())
        if release == "Unassigned":
            release = None
        comment = str(self.plainTextEdit.toPlainText())
        self.ditz.assign_issue(self.ditz_id, release, comment)
        super(AssignDialog, self).accept()

    def reject(self):
        """
        Cancel is clicked on the GUI
        """
        super(AssignDialog, self).reject()

    def ask_assign_issue(self, ditz_id=None):
        """
        Show the dialog (modal)
        to get release name from the user

        Parameters:
        - ditz_id: Ditz item to assign
        """
        if ditz_id != None:
            self.ditz_id = ditz_id
        issue = self.ditz.get_issue_from_cache(ditz_id)
        if not issue:
            raise ApplicationError('Issue not found from cache')
        current_release = issue.release
        index = self.comboBoxRelease.findText(current_release)
        if index >= 0:
            self.comboBoxRelease.setCurrentIndex(index)
        self.exec_()

