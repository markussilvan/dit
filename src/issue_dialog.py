#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker

A dialog for adding and editing Ditz issues
"""

from PyQt4 import QtGui, uic

from common.items import DitzItem
from common.errors import ApplicationError
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
        #TODO: multiple references? form would need changes
        title = str(self.widgetForm.lineEditTitle.text())
        description = str(self.widgetForm.plainTextEditDescription.toPlainText())
        issue_type = self.widgetForm.comboBoxIssueType.currentText()
        status = self.widgetForm.comboBoxStatus.currentText()
        creator = str(self.widgetForm.lineEditCreator.text())
        created = str(self.widgetForm.labelCreatedValue.text())
        release = str(self.widgetForm.comboBoxRelease.currentText())
        references = str(self.widgetForm.lineEditReferences.text())
        identifier = self.ditz_id
        log = ""

        try:
            issue = DitzItem('issue', title, None, issue_type, None, status, None,
                    description, creator, created, release, references, identifier, log)
        except ApplicationError:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "Unable to create issue")
            #TODO: change invalid fields to red or something?
            return

        if self._edit_mode == True:
            self.ditz.edit_issue(issue)
        else:
            self.ditz.add_issue(issue)

        super(IssueDialog, self).accept()

    def reject(self):
        """
        Cancel is clicked on the GUI
        """
        super(IssueDialog, self).reject()

    def ask_new_issue(self):
        """
        Show the dialog and get disposition and a comment from the user
        """
        self.exec_()

    def ask_edit_issue(self, ditz_id):
        """
        Show the dialog filled with data of a given Ditz issue
        """
        issue = self.ditz.get_issue_content(ditz_id)
        if issue == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return

        self._edit_mode = True

        self.widgetForm.lineEditTitle.setText(issue.title)
        self.widgetForm.plainTextEditDescription.insertPlainText(issue.description)
        index = self.widgetForm.comboBoxIssueType.findText(issue.issue_type)
        self.widgetForm.comboBoxIssueType.setCurrentIndex(index)
        index = self.widgetForm.comboBoxStatus.findText(issue.status)
        self.widgetForm.comboBoxStatus.setCurrentIndex(index)
        self.widgetForm.lineEditCreator.setText(issue.creator)
        # two alternative formats allowed for created field
        # needed temporarily until DitzItem always has created as DateTime read from file
        try:
            time_diff = common.utils.time.human_time_diff(issue.created.isoformat(' '))
        except ValueError:
            time_diff = issue.created
        self.widgetForm.labelCreatedValue.setText(time_diff)
        index = self.widgetForm.comboBoxRelease.findText(issue.release)
        self.widgetForm.comboBoxRelease.setCurrentIndex(index)
        self.widgetForm.lineEditReferences.setText(str(issue.references)) #TODO: multiple references
        self.widgetForm.labelIdentifierValue.setText(issue.identifier)
        #TODO: event log, multiple references
        self.exec_()


