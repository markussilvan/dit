#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker

A dialog for close resolution and comment for closing a Ditz issue
"""

from PyQt4 import QtGui, uic

class CloseDialog(QtGui.QDialog):
    """
    A dialog with couple of inputs and Cancel/Ok buttons.
    """
    def __init__(self, ditz, ditz_id):
        """
        Initialize user interface for the dialog

        Parameters:
        - ditz: DitzControl to access data
        - ditz_id: Ditz item to close
        """
        super(CloseDialog, self).__init__()

        self.ditz = ditz
        self.ditz_id = ditz_id

        uic.loadUi('../ui/close_dialog.ui', self)

        for disposition in self.ditz.config.get_valid_issue_dispositions():
            self.comboBox.addItem(disposition)

    def accept(self):
        """
        Ok is pressed on the GUI

        Allowed disposition values:
            "fixed" -> 1
            "won't fix" -> 2
            "reorganized" -> 3
        """
        disposition = self.comboBox.currentIndex()
        comment = str(self.plainTextEdit.toPlainText())
        self.ditz.close_issue(self.ditz_id, disposition, comment)
        super(CloseDialog, self).accept()

    def reject(self):
        """
        Cancel is clicked on the GUI
        """
        super(CloseDialog, self).reject()

    def ask_issue_close(self):
        """
        Show the dialog (modal)
        to get disposition and a comment from the user
        """
        self.exec_()

