#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dit GUI

A GUI frontend for Dit issue tracker

A dialog for close resolution and comment for closing a Dit issue
"""

from PyQt5 import QtWidgets, uic

class CloseDialog(QtWidgets.QDialog):
    """
    A dialog with couple of inputs and Cancel/Ok buttons.
    """
    def __init__(self, dit, dit_id):
        """
        Initialize user interface for the dialog

        Parameters:
        - dit: DitControl to access data
        - dit_id: Dit item to close
        """
        super(CloseDialog, self).__init__()

        self.dit = dit
        self.dit_id = dit_id

        uic.loadUi('../ui/close_dialog.ui', self)

        settings = self.dit.config.get_app_configs()
        for disposition in settings.issue_dispositions:
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
        self.dit.close_issue(self.dit_id, disposition, comment)
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
