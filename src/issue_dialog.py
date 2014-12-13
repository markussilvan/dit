#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker

A dialog for adding and editing Ditz issues
"""

from PyQt4 import QtGui, uic

from comment_dialog import CommentDialog
from common.items import DitzItem
from common.errors import ApplicationError, DitzError
from ditzcontrol import DitzControl
from config import ConfigControl
import common.utils.time

class IssueDialog(QtGui.QDialog):
    """
    A dialog with form input (separate widget) and Cancel/Ok buttons.
    Same form can be used to add new issues or to edit existing ones.
    """
    def __init__(self, ditz, ditz_id=None):
        """
        Initialize user interface for the dialog

        Parameters:
        - ditz: DitzControl to access data
        - ditz_id: Ditz item to edit
        """
        super(IssueDialog, self).__init__()

        self.issue = None

        if not isinstance(ditz, DitzControl):
            raise ApplicationError("Construction failed due to invalid ditz (DitzControl) parameter")

        self.ditz = ditz
        self.ditz_id = ditz_id
        self._edit_mode = False

        uic.loadUi('../ui/issue_dialog.ui', self)
        uic.loadUi('../ui/issue_form_widget.ui', self.widgetForm)

        for state in self.ditz.get_valid_issue_states():
            self.widgetForm.comboBoxStatus.addItem(state)

        for issue_type in self.ditz.get_valid_issue_types():
            self.widgetForm.comboBoxIssueType.addItem(issue_type)

        self.widgetForm.comboBoxRelease.addItem("Unassigned")
        for release in self.ditz.config.get_unreleased_releases():
            self.widgetForm.comboBoxRelease.addItem(release)

        try:
            default_creator = "{} <{}>".format(self.ditz.config.settings.name,
                    self.ditz.config.settings.email)
        except KeyError:
            # leave creator field empty
            pass
        else:
            self.widgetForm.lineEditCreator.setText(default_creator)

    def accept(self):
        """
        Ok is pressed on the GUI

        Check validity of given data.
        Add issue to Ditz or update an existing issue
        """
        self.issue.title = str(self.widgetForm.lineEditTitle.text())
        self.issue.description = str(self.widgetForm.plainTextEditDescription.toPlainText())
        self.issue.issue_type = str(self.widgetForm.comboBoxIssueType.currentText())
        self.issue.status = str(self.widgetForm.comboBoxStatus.currentText())
        self.issue.creator = str(self.widgetForm.lineEditCreator.text())
        self.issue.release = str(self.widgetForm.comboBoxRelease.currentText())
        #TODO: multiple references? form would need changes
        #references = str(self.widgetForm.lineEditReferences.text())

        # ask for a comment
        try:
            dialog = CommentDialog(self.ditz, self.issue.identifier, save=False)
            comment = dialog.ask_comment()
        except DitzError, e:
            QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
            comment = ''

        if self._edit_mode == True:
            self.ditz.edit_issue(self.issue, comment)
        else:
            self.ditz.add_issue(self.issue, comment)

        self.issue = None
        super(IssueDialog, self).accept()

    def reject(self):
        """
        Cancel is clicked on the GUI
        """
        self.issue = None
        super(IssueDialog, self).reject()

    def ask_new_issue(self):
        """
        Show the dialog and get disposition and a comment from the user
        """
        try:
            self.issue = DitzItem('issue', '', None)
        except ApplicationError:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "Unable to create issue")
            return
        self.exec_()

    def ask_edit_issue(self, ditz_id):
        """
        Show the dialog filled with data of a given Ditz issue
        """
        self.issue = self.ditz.get_issue_from_cache(ditz_id)
        if self.issue == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return

        self._edit_mode = True

        self.widgetForm.lineEditTitle.setText(self.issue.title)
        self.widgetForm.plainTextEditDescription.insertPlainText(self.issue.description)
        index = self.widgetForm.comboBoxIssueType.findText(self.issue.issue_type)
        self.widgetForm.comboBoxIssueType.setCurrentIndex(index)
        index = self.widgetForm.comboBoxStatus.findText(self.issue.status)
        self.widgetForm.comboBoxStatus.setCurrentIndex(index)
        self.widgetForm.lineEditCreator.setText(self.issue.creator)
        # two alternative formats allowed for created field
        # needed temporarily until DitzItem always has created as DateTime read from file
        try:
            time_str = common.utils.time.human_time_diff(self.issue.created.isoformat(' '))
        except ValueError:
            time_str = self.issue.created
        self.widgetForm.labelCreatedValue.setText(time_str)
        index = self.widgetForm.comboBoxRelease.findText(self.issue.release)
        self.widgetForm.comboBoxRelease.setCurrentIndex(index)
        self.widgetForm.lineEditReferences.setText(str(self.issue.references)) #TODO: multiple references
        self.widgetForm.labelIdentifierValue.setText(self.issue.identifier)
        #TODO: event log (if needed), multiple references
        self.exec_()


