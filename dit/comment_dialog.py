#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dit GUI

A GUI frontend for Dit issue tracker

A common comment dialog box
"""

import os
from PyQt5 import QtWidgets, uic

class CommentDialog(QtWidgets.QDialog):
    """
    A comment dialog with text input and Cancel/Ok buttons.
    """
    def __init__(self, dit, dit_id, save=False, title='Comment'):
        """
        Initialize user interface for the dialog

        Parameters:
        - dit: DitControl to access data
        - dit_id: Dit item to comment
        - save: Save the comment to Dit
        - title: Dialog window title to show, defaults to "Comment"
        """
        super(CommentDialog, self).__init__()

        self.dit = dit
        self.dit_id = dit_id
        self.save = save
        self.comment = None

        my_path = os.path.dirname(os.path.realpath(__file__))
        uic.loadUi(my_path + '/../ui/comment_dialog.ui', self)

        self.setWindowTitle(title)

    def accept(self):
        """
        Ok is pressed on the GUI
        """
        self.comment = str(self.plainTextEdit.toPlainText())
        if self.save and self.comment != "":
            self.dit.add_comment(self.dit_id, self.comment)
        super(CommentDialog, self).accept()

    def reject(self):
        """
        Cancel is clicked on the GUI
        """
        super(CommentDialog, self).reject()

    def ask_comment(self):
        """
        Show the dialog and get a comment from the user
        If Dit id and comment are given, save the comment to Dit

        Returns:
        - Comment written by the user
        """
        self.exec_()
        return self.comment
