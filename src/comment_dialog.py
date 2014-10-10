#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker

A common comment dialog box
"""

import sys
from PyQt4 import QtGui, uic
#from PyQt4.QtCore import SIGNAL

from ditzcontrol import DitzControl

class CommentDialog(QtGui.QDialog):
    """
    A comment dialog with text input and Cancel/Ok buttons.
    """
    def __init__(self, ditz_id):
        """
        Initialize user interface for the dialog

        Parameters:
        - ditz_id: Ditz item to comment
        """
        super(CommentDialog, self).__init__()

        self.ditzControl = DitzControl()
        self.ditz_id = ditz_id

        uic.loadUi('../ui/comment_dialog.ui', self)

    def accept(self):
        """
        Ok is pressed on the GUI
        """
        comment = str(self.plainTextEdit.toPlainText())
        if comment != "":
            self.ditzControl.add_comment(self.ditz_id, comment)
        super(CommentDialog, self).accept()

    def reject(self):
        """
        Cancel is clicked on the GUI
        """
        super(CommentDialog, self).reject()

    def askComment(self):
        """
        Show the dialog and get a comment from the user
        """
        self.exec_()
