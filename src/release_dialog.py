#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker

A dialog for adding and editing a release
"""

from PyQt4 import QtGui, uic

from ditzcontrol import DitzControl
from common.items import DitzRelease
from common.errors import DitzError, ApplicationError
from comment_dialog import CommentDialog

class ReleaseDialog(QtGui.QDialog):
    """
    A release dialog input fields and Cancel/Ok buttons.
    """
    def __init__(self, ditz, title='Add release'):
        """
        Initialize user interface for the dialog

        Parameters:
        - ditz: DitzControl to access data
        - title: (optional) title for the dialog
        """
        super(ReleaseDialog, self).__init__()

        if not isinstance(ditz, DitzControl):
            raise ApplicationError("Construction failed due to invalid ditz (DitzControl) parameter")

        self.ditz = ditz
        self.release = None

        uic.loadUi('../ui/release_dialog.ui', self)

        self.setWindowTitle(title)

        for state in self.ditz.config.get_valid_release_states():
            self.comboBoxStatus.addItem(state)

    def accept(self):
        """
        Ok is pressed on the GUI
        """
        # check if new or edited release
        if not self.release:
            old_title = None
            self.release = DitzRelease(str(self.lineEditName.text()), "Release")
            action = 'created'
        else:
            old_title = self.release.title
            self.release.title = str(self.lineEditName.text())
            self.release.name = "Release"
            action = 'edited'

        self.release.status = str(self.comboBoxStatus.currentText())
        self.release.release_time = str(self.labelReleaseTimeValue.text())

        # ask for a comment
        try:
            dialog = CommentDialog(self.ditz, None, save=False,
                    title='Comment for release')
            comment = dialog.ask_comment()
        except DitzError, e:
            QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
            comment = ''

        settings = self.ditz.config.get_ditz_configs()
        creator = '{} <{}>'.format(settings.name, settings.email)
        self.release.add_log_entry(None, action, creator, comment)

        # save changes
        if old_title and old_title != self.release.title:
            self.ditz.config.projectconfig.set_release(self.release, old_name=old_title)
        else:
            self.ditz.config.projectconfig.set_release(self.release)
        self.ditz.config.projectconfig.write_config_file()

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
        - a DitzRelease containing given information
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
        - an edited DitzRelease
        """
        release = self.ditz.get_release_from_cache(release_name)
        if not release:
            raise ApplicationError('Release not found from cache')

        self.release = release
        self.lineEditName.setText(self.release.title)

        index = self.comboBoxStatus.findText(self.release.status)
        self.comboBoxStatus.setCurrentIndex(index)

        if self.release.status == 'released':
            self.labelReleaseTimeValue.setText(str(self.release.release_time))
        else:
            self.labelReleaseTimeValue.setText("-")

        self.exec_()
        return self.release

