#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker

A common issue reference dialog box
"""

from PyQt5 import QtWidgets, uic

from comment_dialog import CommentDialog
from common.errors import ApplicationError, DitzError
from ditzcontrol import DitzControl

class ReferenceDialog(QtWidgets.QDialog):
    """
    A reference dialog with text input and Cancel/Ok buttons.
    """
    def __init__(self, ditz, ditz_id=None, save=True, reference_text=None):
        """
        Initialize user interface for the dialog

        Parameters:
        - ditz: DitzControl to use to access data
        - ditz_id: Ditz item to reference
        - save: Save the reference to Ditz
        - reference_text: Preset text for the reference to add, used when editing a reference
        """
        super(ReferenceDialog, self).__init__()

        if not isinstance(ditz, DitzControl):
            raise ApplicationError("Construction failed due to invalid ditz (DitzControl) parameter")

        self.ditz = ditz
        self.ditz_id = ditz_id
        self.save = save
        self.reference = reference_text

        uic.loadUi('../ui/reference_dialog.ui', self)

    def accept(self):
        """
        Ok is pressed on the GUI
        """
        self.reference = str(self.lineEdit.text())
        if self.reference != "" and self.save is True and self.ditz_id is not None:
            # ask for a comment
            try:
                dialog = CommentDialog(self.ditz, self.ditz_id, save=False,
                        title='Comment to add with the reference')
                comment = dialog.ask_comment()
            except DitzError as e:
                QtWidgets.QMessageBox.warning(self, "Ditz error", e.error_message)
                comment = ''
            # add the reference
            self.ditz.add_reference(self.ditz_id, self.reference, comment)
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
        - Reference written by the user
        """
        if self.reference:
            self.lineEdit.setText(self.reference)
        self.exec_()
        return self.reference
