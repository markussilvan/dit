#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dit GUI

A GUI frontend for Dit issue tracker

A dialog for adding and editing a release
"""

from PyQt5 import QtWidgets, uic

from ditcontrol import DitControl
from common.items import DitRelease
from common.errors import DitError, ApplicationError
from comment_dialog import CommentDialog
from common import constants


class ReleaseDialog(QtWidgets.QDialog):
    """
    A release dialog input fields and Cancel/Ok buttons.
    """
    def __init__(self, dit, title='Add release'):
        """
        Initialize user interface for the dialog

        Parameters:
        - dit: DitControl to access data
        - title: (optional) title for the dialog
        """
        super(ReleaseDialog, self).__init__()

        if not isinstance(dit, DitControl):
            raise ApplicationError("Construction failed due to invalid dit (DitControl) parameter")

        self.dit = dit
        self.release = None

        uic.loadUi('../ui/release_dialog.ui', self)

        self.setWindowTitle(title)

        for state in self.dit.config.get_valid_release_states():
            self.comboBoxStatus.addItem(state)

    def accept(self):
        """
        Ok is pressed on the GUI
        """
        # check if new or edited release
        if not self.release:
            old_title = None
            self.release = DitRelease(str(self.lineEditName.text()), "Release")
            action = 'created'
        else:
            old_title = self.release.title
            self.release.title = str(self.lineEditName.text())
            self.release.name = "Release"
            action = 'edited'

        old_status = self.release.status
        self.release.status = str(self.comboBoxStatus.currentText())

        # check if release status was changed to 'released' and cancel the process if required
        if old_status != self.release.status and self.release.status == constants.release_states.RELEASED:
            message = "Use 'make release' to release a release.\nNot changing state to 'released'."
            QtWidgets.QMessageBox.warning(self, "Dit GUI warning", message)
            self.release.status = old_status
            return

        # ask for a comment
        try:
            dialog = CommentDialog(self.dit, None, save=False,
                    title='Comment for release')
            comment = dialog.ask_comment()
        except DitError as e:
            QtWidgets.QMessageBox.warning(self, "Dit error", e.error_message)
            comment = ''

        creator = self.dit.config.get_default_creator()
        self.release.add_log_entry(None, action, creator, comment)

        # save changes
        if old_title and old_title != self.release.title:
            self.dit.config.projectconfig.set_release(self.release, old_name=old_title)
            issues = self.dit.get_issues_by_release(old_title)
            for issue in issues:
                self.dit.assign_issue(issue.identifier, self.release.title, 'Release renamed.')
        else:
            self.dit.config.projectconfig.set_release(self.release)
        if self.dit.config.projectconfig.write_config_file() is False:
            QtWidgets.QMessageBox.warning(self, "Error",
                    "Saving project configuration file failed")
        else:
            super(ReleaseDialog, self).accept()

    def reject(self):
        """
        Cancel is clicked on the GUI
        """
        self.release = None
        super(ReleaseDialog, self).reject()

    def add_release(self):
        """
        Show the dialog and get release information from user

        Returns:
        - a DitRelease containing given information
        """
        self.release = None
        self.exec_()
        return self.release

    def edit_release(self, release_name):
        """
        Show the dialog and get changes to relese information from user

        Parameters:
        - release_name: name of the release to edit

        Returns:
        - an edited DitRelease
        """
        release = self.dit.get_release_from_cache(release_name)
        if not release:
            raise ApplicationError('Release not found from cache')

        self.release = release
        self.lineEditName.setText(self.release.title)

        index = self.comboBoxStatus.findText(self.release.status)
        self.comboBoxStatus.setCurrentIndex(index)

        if self.release.status == constants.release_states.RELEASED:
            self.labelReleaseTimeValue.setText(str(self.release.release_time))
        else:
            self.labelReleaseTimeValue.setText("")

            # don't allow making a release from this dialog
            index = self.comboBoxStatus.findText(constants.release_states.RELEASED)
            self.comboBoxStatus.removeItem(index)
            #model_index = self.comboBoxStatus.model().index(index, 0)
            #self.comboBoxStatus.model().setData(model_index, QtCore.QVariant(0), QtCore.Qt.UserRole-1)

        self.exec_()
        return self.release
