#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker

A dialog for adding and editing Ditz issues
"""

from PyQt4 import QtGui, uic
from PyQt4.QtCore import SIGNAL

from reference_dialog import ReferenceDialog
from comment_dialog import CommentDialog
from common.items import DitzIssue
from common.errors import ApplicationError, DitzError
from ditzcontrol import DitzControl
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

        settings = self.ditz.config.get_ditz_configs()

        for state in self.ditz.config.get_valid_issue_states():
            self.widgetForm.comboBoxStatus.addItem(state)

        for issue_type in self.ditz.config.get_valid_issue_types():
            self.widgetForm.comboBoxIssueType.addItem(issue_type)

        self.widgetForm.comboBoxRelease.addItem("Unassigned")
        for release in self.ditz.config.get_releases('unreleased', True):
            self.widgetForm.comboBoxRelease.addItem(release)

        try:
            default_creator = "{} <{}>".format(settings.name, settings.email)
        except KeyError:
            # leave creator field empty
            pass
        else:
            self.widgetForm.lineEditCreator.setText(default_creator)

        self._connect_actions()

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

        self.issue.references = []
        for i in range(self.widgetForm.listWidgetReferences.count()):
            reference = str(self.widgetForm.listWidgetReferences.item(i).text())
            self.issue.references.append(reference)

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
            self.issue = DitzIssue('', None)
        except ApplicationError:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "Unable to create issue")
            return

        settings = self.ditz.config.get_app_configs()
        default_issue_type = settings.default_issue_type
        index = self.widgetForm.comboBoxIssueType.findText(default_issue_type)
        if index >= 0:
            self.widgetForm.comboBoxIssueType.setCurrentIndex(index)

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

        # two alternative formats allowed for created field (just in case)
        try:
            time_str = common.utils.time.human_time_diff(self.issue.created.isoformat(' '))
        except ValueError:
            time_str = self.issue.created
        self.widgetForm.labelCreatedValue.setText(time_str)

        index = self.widgetForm.comboBoxRelease.findText(self.issue.release)
        self.widgetForm.comboBoxRelease.setCurrentIndex(index)

        self.widgetForm.listWidgetReferences.clear()
        for reference in self.issue.references:
            self.widgetForm.listWidgetReferences.addItem(reference)

        self.widgetForm.labelIdentifierValue.setText(self.issue.identifier)
        self.exec_()

    def _connect_actions(self):
        """
        Connect custom actions used on this dialog

        Ok/Cancel are already connected to accept/reject.
        """
        self.widgetForm.pushButtonAdd.clicked.connect(self._add_reference)
        self.widgetForm.pushButtonEdit.clicked.connect(self._edit_reference)
        self.widgetForm.pushButtonRemove.clicked.connect(self._remove_reference)
        self.widgetForm.listWidgetReferences.clicked.connect(self._set_button_states)
        self.connect(self.widgetForm.listWidgetReferences,
                SIGNAL("itemSelectionChanged()"),
                self._set_button_states)

    def _set_button_states(self):
        """
        Enable the correct buttons

        Depending on selection on the references list,
        different buttons need to be enabled.
        """
        if self._get_selected_reference_text() != None:
            # a reference is selected
            self.widgetForm.pushButtonEdit.setEnabled(True)
            self.widgetForm.pushButtonRemove.setEnabled(True)
        else:
            # no refererence selected
            self.widgetForm.pushButtonEdit.setEnabled(False)
            self.widgetForm.pushButtonRemove.setEnabled(False)

    def _add_reference(self):
        """
        Add a new reference to the issue being added or edited.
        """
        dialog = ReferenceDialog(self.ditz, save=False)
        reference = dialog.ask_reference()

        if reference != None and reference != '':
            self.widgetForm.listWidgetReferences.addItem(reference)

    def _edit_reference(self):
        """
        Change the selected reference text.
        """
        reference = self._get_selected_reference_text()
        if reference != None:
            for selected in self.widgetForm.listWidgetReferences.selectedItems():
                old_text = str(selected.text())
                dialog = ReferenceDialog(self.ditz, save=False, reference_text=old_text)
                edited_text = dialog.ask_reference()
                selected.setText(edited_text)
                break

    def _remove_reference(self):
        """
        Remove the selected reference from the issues being added or edited.
        """
        reference = self._get_selected_reference_text()
        if reference != None:
            for selected in self.widgetForm.listWidgetReferences.selectedItems():
                selected_row = self.widgetForm.listWidgetReferences.row(selected)
                self.widgetForm.listWidgetReferences.takeItem(selected_row)

    def _get_selected_reference_text(self):
        item = self.widgetForm.listWidgetReferences.currentItem()
        if not item:
            return None
        text = str(item.text())
        if len(text) == 0:
            return None
        return text

