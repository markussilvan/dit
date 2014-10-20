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

class CommentDialog(QtGui.QDialog):
    """
    A comment dialog with text input and Cancel/Ok buttons.
    """
    def __init__(self, ditz_id, save=False):
        """
        Initialize user interface for the dialog

        Parameters:
        - ditz_id: Ditz item to comment
        - save: Save the comment to Ditz
        """
        super(CommentDialog, self).__init__()

        self.ditz = DitzControl()
        self.ditz_id = ditz_id
        self.save = save
        self.comment = None

        uic.loadUi('../ui/comment_dialog.ui', self)

    def accept(self):
        """
        Ok is pressed on the GUI
        """
        self.comment = str(self.plainTextEdit.toPlainText())
        if self.save and self.comment != "":
            self.ditz.add_comment(self.ditz_id, self.comment)
        super(CommentDialog, self).accept()

    def reject(self):
        """
        Cancel is clicked on the GUI
        """
        super(CommentDialog, self).reject()

    def ask_comment(self):
        """
        Show the dialog and get a comment from the user
        If Ditz id and comment are given, save the comment to Ditz

        Returns:
        - Comment written by the user
        """
        self.exec_()
        return self.comment
