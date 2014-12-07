#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker

A common issue reference dialog box
"""

from PyQt4 import QtGui, uic

from ditzcontrol import DitzControl

class ReferenceDialog(QtGui.QDialog):
    """
    A reference dialog with text input and Cancel/Ok buttons.
    """
    def __init__(self, ditz, ditz_id):
        """
        Initialize user interface for the dialog

        Parameters:
        - ditz: DitzControl to use to access data
        - ditz_id: Ditz item to reference
        - save: Save the reference to Ditz
        """
        super(ReferenceDialog, self).__init__()

        self.ditz = ditz
        self.ditz_id = ditz_id
        self.reference = None

        uic.loadUi('../ui/reference_dialog.ui', self)

    def accept(self):
        """
        Ok is pressed on the GUI
        """
        self.reference = str(self.lineEdit.text())
        if self.reference != "":
            self.ditz.add_reference(self.ditz_id, self.reference)
        super(ReferenceDialog, self).accept()

    def reject(self):
        """
        Cancel is clicked on the GUI
        """
        super(ReferenceDialog, self).reject()

    def ask_reference(self):
        """
        Show the dialog and get a reference from the user
        If Ditz id and reference are given, save the comment to Ditz

        Returns:
        - Comment written by the user
        """
        self.exec_()
        return self.reference
