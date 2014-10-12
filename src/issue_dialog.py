#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker

A dialog for adding and editing Ditz issues
"""

import sys
from PyQt4 import QtGui, uic

from ditzcontrol import DitzControl

class IssueDialog(QtGui.QDialog):
    """
    A dialog with form input (separate widget) and Cancel/Ok buttons.
    Same form can be used to add new issues or to edit existing ones.
    """
    def __init__(self, ditz_id=None):
        """
        Initialize user interface for the dialog

        Parameters:
        - ditz_id: Ditz item to edit
        """
        super(IssueDialog, self).__init__()

        self.ditzControl = DitzControl()
        self.ditz_id = ditz_id

        uic.loadUi('../ui/form_dialog.ui', self)
        uic.loadUi('../ui/issue_form_widget.ui', self.widgetForm)

    def accept(self):
        """
        Ok is pressed on the GUI

        Check validity of given data.
        Add issue to Ditz or update an existing issue
        """
        #TODO: encapsulate all those field into DitzIssue objects (add those fields to DitzIssue)
        #TODO: read all the fields from the form to a DitzIssue
        description = str(self.plainTextEditDescription.toPlainText())
        #status = self.comboBoxStatus.currentIndex() + 1
        #if self.ditz_id == None:
        #    self.ditzControl.add_issue(header, description, issue_type, status, creator, release, references)
        super(IssueDialog, self).accept()

    def reject(self):
        """
        Cancel is clicked on the GUI
        """
        super(IssueDialog, self).reject()

    def ask_new_issue(self):
        """
        Show the dialog and get disposition and a comment from the user
        """
        self.exec_()

    def ask_edit_issue(self, ditz_id):
        """
        Show the dialog filled with data of a given Ditz issue
        """
        #TODO: load item data from ditz
        self.exec_()


