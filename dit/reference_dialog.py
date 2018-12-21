#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dit GUI

A GUI frontend for Dit issue tracker

A common issue reference dialog box
"""

import os

from PyQt5 import QtWidgets, uic

from comment_dialog import CommentDialog
from common.errors import ApplicationError, DitError
from ditcontrol import DitControl

class ReferenceDialog(QtWidgets.QDialog):
    """
    A reference dialog with text input and Cancel/Ok buttons.
    """
    def __init__(self, dit, dit_id=None, save=True, reference_text=None):
        """
        Initialize user interface for the dialog

        Parameters:
        - dit: DitControl to use to access data
        - dit_id: Dit item to reference
        - save: Save the reference to Dit
        - reference_text: Preset text for the reference to add, used when editing a reference
        """
        super(ReferenceDialog, self).__init__()

        if not isinstance(dit, DitControl):
            raise ApplicationError("Construction failed due to invalid dit parameter")

        self.dit = dit
        self.dit_id = dit_id
        self.save = save
        self.reference = reference_text

        my_path = os.path.dirname(os.path.realpath(__file__))
        uic.loadUi(my_path + '/../ui/reference_dialog.ui', self)

    def accept(self):
        """
        Ok is pressed on the GUI
        """
        self.reference = str(self.lineEdit.text())
        if self.reference != "" and self.save is True and self.dit_id is not None:
            # ask for a comment
            try:
                dialog = CommentDialog(self.dit, self.dit_id, save=False,
                        title='Comment to add with the reference')
                comment = dialog.ask_comment()
            except DitError as e:
                QtWidgets.QMessageBox.warning(self, "Dit error", e.error_message)
                comment = ''
            # add the reference
            self.dit.add_reference(self.dit_id, self.reference, comment)
        super(ReferenceDialog, self).accept()

    def reject(self):
        """
        Cancel is clicked on the GUI
        """
        super(ReferenceDialog, self).reject()

    def ask_reference(self):
        """
        Show the dialog and get a reference from the user
        If Dit id and reference are given, save the comment to Dit

        Returns:
        - Reference written by the user
        """
        if self.reference:
            self.lineEdit.setText(self.reference)
        self.exec_()
        return self.reference
