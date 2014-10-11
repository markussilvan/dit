#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker

A common comment dialog box
"""

import sys
from PyQt4 import QtGui, uic

from ditzcontrol import DitzControl

class CloseDialog(QtGui.QDialog):
    """
    A comment dialog with text input and Cancel/Ok buttons.
    """
    def __init__(self, ditz_id):
        """
        Initialize user interface for the dialog

        Parameters:
        - ditz_id: Ditz item to comment
        """
        super(CloseDialog, self).__init__()

        self.ditzControl = DitzControl()
        self.ditz_id = ditz_id

        uic.loadUi('../ui/close_dialog.ui', self)

    def accept(self):
        """
        Ok is pressed on the GUI

        Allowed disposition values:
            "fixed" -> 1
            "won't fix" -> 2
            "reorganized" -> 3
        """
        disposition = self.comboBox.currentIndex() + 1
        comment = str(self.plainTextEdit.toPlainText())
        self.ditzControl.close_issue(self.ditz_id, disposition, comment)
        super(CloseDialog, self).accept()

    def reject(self):
        """
        Cancel is clicked on the GUI
        """
        super(CloseDialog, self).reject()

    def askIssueClose(self):
        """
        Show the dialog and get disposition and a comment from the user
        """
        self.exec_()

