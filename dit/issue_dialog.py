#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dit GUI

A GUI frontend for Dit issue tracker

A dialog for adding and editing Dit issues
"""

from PyQt5 import QtWidgets, uic

from reference_dialog import ReferenceDialog
from comment_dialog import CommentDialog
from common.items import DitIssue
from common.errors import ApplicationError, DitError
from common import constants
import common.utils.time
from ditcontrol import DitControl

class IssueDialog(QtWidgets.QDialog):
    """
    A dialog with form input (separate widget) and Cancel/Ok buttons.
    Same form can be used to add new issues or to edit existing ones.
    """
    def __init__(self, dit, dit_id=None):
        """
        Initialize user interface for the dialog

        Parameters:
        - dit: DitControl to access data
        - dit_id: Dit item to edit
        """
        super(IssueDialog, self).__init__()

        self.issue = None

        if not isinstance(dit, DitControl):
            raise ApplicationError("Construction failed due to invalid dit (DitControl) parameter")

        self.dit = dit
        self.dit_id = dit_id
        self._edit_mode = False

        uic.loadUi('../ui/issue_dialog.ui', self)
        uic.loadUi('../ui/issue_form_widget.ui', self.widgetForm)

        settings = self.dit.config.get_app_configs()

        for state in self.dit.config.get_valid_issue_states():
            self.widgetForm.comboBoxStatus.addItem(state)

        for issue_type in settings.issue_types:
            self.widgetForm.comboBoxIssueType.addItem(issue_type)

        self.widgetForm.comboBoxRelease.addItem(constants.releases.UNASSIGNED)
        for release in self.dit.config.get_releases(constants.release_states.UNRELEASED, True):
            self.widgetForm.comboBoxRelease.addItem(release)

        default_creator = self.dit.config.get_default_creator()
        self.widgetForm.lineEditCreator.setText(default_creator)

        self._connect_actions()

    def accept(self):
        """
        Ok is pressed on the GUI

        Check validity of given data.
        Add issue to Dit or update an existing issue
        """
        self.issue.title = str(self.widgetForm.lineEditTitle.text())
        self.issue.description = str(self.widgetForm.plainTextEditDescription.toPlainText())
        self.issue.issue_type = str(self.widgetForm.comboBoxIssueType.currentText())
        self.issue.status = str(self.widgetForm.comboBoxStatus.currentText())
        self.issue.creator = str(self.widgetForm.lineEditCreator.text())
        release = str(self.widgetForm.comboBoxRelease.currentText())
        if release == constants.releases.UNASSIGNED:
            release = None
        self.issue.release = release

        self.issue.references = []
        for i in range(self.widgetForm.listWidgetReferences.count()):
            reference = str(self.widgetForm.listWidgetReferences.item(i).text())
            self.issue.references.append(reference)

        # ask for a comment
        try:
            dialog = CommentDialog(self.dit, self.issue.identifier, save=False)
            comment = dialog.ask_comment()
        except DitError as e:
            QtWidgets.QMessageBox.warning(self, "Dit error", e.error_message)
            comment = ''

        if self._edit_mode is True:
            self.dit.edit_issue(self.issue, comment)
        else:
            self.dit.add_issue(self.issue, comment)

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
        Show the dialog and get issue information from user
        """
        try:
            self.issue = DitIssue('', None)
        except ApplicationError:
            QtWidgets.QMessageBox.warning(self, "dit-gui error", "Unable to create issue")
            return

        settings = self.dit.config.get_app_configs()
        default_issue_type = settings.default_issue_type
        index = self.widgetForm.comboBoxIssueType.findText(default_issue_type)
        if index >= 0:
            self.widgetForm.comboBoxIssueType.setCurrentIndex(index)

        self.exec_()

    def ask_edit_issue(self, dit_id):
        """
        Show the dialog filled with data of a given Dit issue
        """
        self.issue = self.dit.get_issue_from_cache(dit_id)
        if self.issue is None:
            QtWidgets.QMessageBox.warning(self, "dit-gui error", "No issue selected")
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
        self.widgetForm.listWidgetReferences.itemSelectionChanged.connect(self._set_button_states)

    def _set_button_states(self):
        """
        Enable the correct buttons

        Depending on selection on the references list,
        different buttons need to be enabled.
        """
        if self._get_selected_reference_text() is not None:
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
        dialog = ReferenceDialog(self.dit, save=False)
        reference = dialog.ask_reference()

        if reference not in [None, ""]:
            self.widgetForm.listWidgetReferences.addItem(reference)

    def _edit_reference(self):
        """
        Change the selected reference text.
        """
        reference = self._get_selected_reference_text()
        if reference is not None:
            for selected in self.widgetForm.listWidgetReferences.selectedItems():
                old_text = str(selected.text())
                dialog = ReferenceDialog(self.dit, save=False, reference_text=old_text)
                edited_text = dialog.ask_reference()
                selected.setText(edited_text)
                break

    def _remove_reference(self):
        """
        Remove the selected reference from the issues being added or edited.
        """
        reference = self._get_selected_reference_text()
        if reference is not None:
            for selected in self.widgetForm.listWidgetReferences.selectedItems():
                selected_row = self.widgetForm.listWidgetReferences.row(selected)
                self.widgetForm.listWidgetReferences.takeItem(selected_row)

    def _get_selected_reference_text(self):
        item = self.widgetForm.listWidgetReferences.currentItem()
        if not item:
            return None
        text = str(item.text())
        if text == "":
            return None
        return text
