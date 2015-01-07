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
        if not self.release:
            self.release = DitzRelease(str(self.lineEditName.text()), "Release")
        else:
            self.release.title = str(self.lineEditName.text())
            self.release.name = "Release"

        self.release.status = str(self.comboBoxStatus.currentText())
        self.release.release_time = str(self.labelReleaseTimeValue.text())

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

