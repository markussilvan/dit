#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dit GUI

A GUI frontend for Dit issue tracker

A dialog for assigning an issue to a release
"""

import os

from PyQt5 import QtWidgets, uic

from ditcontrol import DitControl
from common.errors import ApplicationError
from common import constants

class AssignDialog(QtWidgets.QDialog):
    """
    A dialog with couple of inputs and Cancel/Ok buttons.
    """
    def __init__(self, dit, dit_id=None):
        """
        Initialize user interface for the dialog

        Parameters:
        - dit: DitControl to access data
        - dit_id: Dit item to assign
        """
        super(AssignDialog, self).__init__()

        if not isinstance(dit, DitControl):
            raise ApplicationError("Construction failed due to invalid dit (DitControl) parameter")

        self.dit = dit
        self.dit_id = dit_id

        my_path = os.path.dirname(os.path.realpath(__file__))
        uic.loadUi(my_path + '/../ui/assign_dialog.ui', self)

        self.comboBoxRelease.addItem(constants.releases.UNASSIGNED)
        for release in self.dit.config.get_releases(constants.release_states.UNRELEASED, True):
            self.comboBoxRelease.addItem(release)

    def accept(self):
        """
        Ok is pressed on the GUI

        Given issue is now assigned to the selected release.
        """
        release = str(self.comboBoxRelease.currentText())
        if release == constants.releases.UNASSIGNED:
            release = None
        comment = str(self.plainTextEdit.toPlainText())
        self.dit.assign_issue(self.dit_id, release, comment)
        super(AssignDialog, self).accept()

    def reject(self):
        """
        Cancel is clicked on the GUI
        """
        super(AssignDialog, self).reject()

    def ask_assign_issue(self, dit_id=None):
        """
        Show the dialog (modal)
        to get release name from the user

        Parameters:
        - dit_id: Dit item to assign
        """
        if dit_id is not None:
            self.dit_id = dit_id
        issue = self.dit.get_issue_from_cache(dit_id)
        if not issue:
            raise ApplicationError('Issue not found from cache')
        current_release = issue.release
        if current_release is None:
            current_release = constants.releases.UNASSIGNED
        index = self.comboBoxRelease.findText(current_release)
        if index >= 0:
            self.comboBoxRelease.setCurrentIndex(index)
        self.exec_()
