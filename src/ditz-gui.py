#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ditz-gui

A GUI frontend for Ditz issue tracker

Ditz is a simple, light-weight distributed issue tracker designed
to work with distributed version control systems like git, darcs,
Mercurial, and Bazaar. It can also be used with centralized systems
like SVN. Ditz maintains an issue database directory on disk, with
files written in a line-based and human-editable format. This
directory can be kept under version control, alongside project code.
"""

import sys
from PyQt4 import QtGui, uic
from PyQt4.QtCore import SIGNAL, QModelIndex

from common.errors import DitzError
from config import ConfigControl
from ditzcontrol import DitzControl
from comment_dialog import CommentDialog
from reference_dialog import ReferenceDialog
from issue_dialog import IssueDialog
from close_dialog import CloseDialog
from settings_dialog import SettingsDialog
from assign_dialog import AssignDialog

class DitzGui(QtGui.QMainWindow):
    """
    The main window
    """
    def __init__(self):
        """
        Initialize user interface
        """
        super(DitzGui, self).__init__()

        self.config = ConfigControl()
        self.config.read_config_file()
        self.ditz = DitzControl(self.config)

        uic.loadUi('../ui/main_window.ui', self)

        self.reload_data()

        self.connect(self.listWidgetDitzItems,
                SIGNAL('customContextMenuRequested(const QPoint &)'),
                self.context_menu)

        self.actionCommentIssue = None
        self.actionStartWork = None
        self.actionStopWork = None
        self.actionAddReference = None
        self.actionEditIssue = None
        self.actionNewIssue = None
        self.actionCloseIssue = None
        self.actionDropIssue = None
        self.actionAssignIssue = None
        self.actionMakeRelease = None
        self.actionOpenSettings = None

        self.create_actions()
        self.build_toolbar_menu()
        self.enable_valid_actions()

        self.show_main_window()

    def show_main_window(self):
        """
        Show the main application window
        """
        self.resize(800, 500)
        self.center()
        self.setWindowTitle('Ditz GUI')
        self.setWindowIcon(QtGui.QIcon('../graphics/ditz_gui_icon.png'))
        self.show()

    def create_actions(self):
        # create action objects
        self.actionNewIssue = QtGui.QAction(QtGui.QIcon('../graphics/issue/new.png'), 'New Issue', self)
        self.actionEditIssue = QtGui.QAction(QtGui.QIcon('../graphics/issue/edit.png'), 'Edit Issue', self)
        self.actionCommentIssue = QtGui.QAction(QtGui.QIcon('../graphics/issue/comment.png'), 'Comment Issue', self)
        self.actionStartWork = QtGui.QAction(QtGui.QIcon('../graphics/issue/start.png'), 'Start working', self)
        self.actionStopWork = QtGui.QAction(QtGui.QIcon('../graphics/issue/stop.png'), 'Stop working', self)
        self.actionCloseIssue = QtGui.QAction(QtGui.QIcon('../graphics/issue/close.png'), 'Close issue', self)
        self.actionDropIssue = QtGui.QAction(QtGui.QIcon('../graphics/issue/drop.png'), 'Drop issue', self)
        self.actionAssignIssue = QtGui.QAction(QtGui.QIcon('../graphics/issue/assign.png'), 'Assign Issue to a release', self)
        self.actionAddReference = QtGui.QAction(QtGui.QIcon('../graphics/issue/add_reference.png'),
                'Add reference', self)

        #self.actionAddRelease = QtGui.QAction(QtGui.QIcon('../graphics/release/add_release.png'),
        #       'Add release', self)
        self.actionMakeRelease = QtGui.QAction(QtGui.QIcon('../graphics/release/make_release.png'),
                'Make release', self)

        self.actionOpenSettings = QtGui.QAction(QtGui.QIcon('../graphics/release/settings.png'), 'Settings', self)

        # icons visible in custom context menu of items list view
        self.actionNewIssue.iconVisibleInMenu = True
        self.actionEditIssue.iconVisibleInMenu = True
        self.actionCommentIssue.iconVisibleInMenu = True
        self.actionStartWork.iconVisibleInMenu = True
        self.actionStopWork.iconVisibleInMenu = True
        self.actionCloseIssue.iconVisibleInMenu = True
        self.actionDropIssue.iconVisibleInMenu = True
        self.actionAssignIssue.iconVisibleInMenu = True
        self.actionAddReference.iconVisibleInMenu = True
        #self.actionAddRelease.iconVisibleInMenu = True
        self.actionMakeRelease.iconVisibleInMenu = True
        self.actionOpenSettings.iconVisibleInMenu = True

        # connect
        self.actionNewIssue.triggered.connect(self.new_issue)
        self.actionEditIssue.triggered.connect(self.edit_issue)
        self.actionCommentIssue.triggered.connect(self.comment_issue)
        self.actionStartWork.triggered.connect(self.start_work)
        self.actionStopWork.triggered.connect(self.stop_work)
        self.actionCloseIssue.triggered.connect(self.close_issue)
        self.actionDropIssue.triggered.connect(self.drop_issue)
        self.actionAssignIssue.triggered.connect(self.assign_issue)
        self.actionAddReference.triggered.connect(self.add_reference)

        ##self.actionAddRelease.triggered.connect(self.add_release)
        self.actionMakeRelease.triggered.connect(self.make_release)

        self.actionOpenSettings.triggered.connect(self.open_settings)

        # connect qt creator created actions
        self.actionReload.triggered.connect(self.reload_data)
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionExit.triggered.connect(self.quit_application)
        self.listWidgetDitzItems.clicked.connect(self.show_item)

    def enable_valid_actions(self):
        """
        Enabled (toolbar) actions that are valid at the moment.
        Only common actions and actions valid for an item currently selected
        should be enabled. Others are disabled.
        """
        item_type = self._get_selected_item_type()
        if item_type == 'issue':
            status = self._get_selected_issue_status()
            if status == 'in progress':
                start_state = False
            else:
                start_state = True
            self._set_issue_actions(True, start_state)
            self._set_release_actions(False)
        elif item_type == 'release':
            self._set_issue_actions(False)
            self._set_release_actions(True)
        else:
            self._set_issue_actions(False)
            self._set_release_actions(False)

        #self.actionOpenSettings.setEnabled(True)

    def _set_issue_actions(self, state, start_state=True):
        self.actionEditIssue.setEnabled(state)
        self.actionCommentIssue.setEnabled(state)
        if state == True:
            self.actionStartWork.setEnabled(start_state)
            self.actionStopWork.setEnabled(not start_state)
        else:
            self.actionStartWork.setEnabled(state)
            self.actionStopWork.setEnabled(state)
        self.actionCloseIssue.setEnabled(state)
        self.actionDropIssue.setEnabled(state)
        self.actionAssignIssue.setEnabled(state)
        self.actionAddReference.setEnabled(state)

    def _set_release_actions(self, state):
        #self.actionAddRelease.setEnabled(state)
        self.actionMakeRelease.setEnabled(state)

    def center(self):
        """
        Center the window to screen
        """
        rect = self.frameGeometry()
        desktop_center = QtGui.QDesktopWidget().availableGeometry().center()
        rect.moveCenter(desktop_center)
        self.move(rect.topLeft())

    def context_menu(self):
        # pylint: disable=W0108
        ditz_id = self._get_selected_issue_id()
        item_type = self._get_selected_item_type()
        status = self._get_selected_issue_status()
        menu = QtGui.QMenu(self)
        if item_type == 'issue':
            menu.addAction(self.actionNewIssue)
            # custom actions used here to get custom menu texts
            menu.addAction("Edit " + ditz_id, lambda:self.edit_issue())
            menu.addAction("Comment " + ditz_id, lambda:self.comment_issue())
            menu.addAction("Add reference to " + ditz_id, lambda:self.add_reference())
            if status != "in progress" and status != "started":
                menu.addAction("Start work on " + ditz_id, lambda:self.start_work())
            else:
                menu.addAction("Stop work on " + ditz_id, lambda:self.stop_work())
            menu.addAction("Close " + ditz_id, lambda:self.close_issue())
            menu.addAction("Drop " + ditz_id, lambda:self.drop_issue())
            menu.addAction("Assign " + ditz_id, lambda:self.assign_issue())
        elif item_type == 'release':
            menu.addAction(self.actionNewIssue)
            menu.addAction(self.actionMakeRelease)
            #TODO: add issue directly to this release?
            #TODO: make release?
            #TODO: drop release?
            # or just option to open releases dialog
        else:
            # empty lines
            menu.addAction(self.actionNewIssue)
        menu.exec_(QtGui.QCursor.pos())

    def build_toolbar_menu(self):
        self.toolBar.addAction(self.actionNewIssue)
        self.toolBar.addAction(self.actionEditIssue)
        self.toolBar.addAction(self.actionCommentIssue)
        self.toolBar.addAction(self.actionStartWork)
        self.toolBar.addAction(self.actionStopWork)
        self.toolBar.addAction(self.actionCloseIssue)
        self.toolBar.addAction(self.actionDropIssue)

    def reload_data(self, ditz_id=None):
        data = self.ditz.get_items()
        self.listWidgetDitzItems.clear()
        for item in data:
            if item.item_type == 'release' and self.listWidgetDitzItems.count() > 0:
                # add one empty line as a spacer (except on the first line)
                self.listWidgetDitzItems.addItem("")
            if item.name == None:
                title = item.title
            else:
                title = "{:<13}{}".format(item.name, item.title)
            self.listWidgetDitzItems.addItem(title)

            # set icon to the added item
            list_item = self.listWidgetDitzItems.item(self.listWidgetDitzItems.count() - 1)
            if item.item_type == 'issue':
                if item.status == 'unstarted':
                    list_item.setIcon(QtGui.QIcon('../graphics/list/balls/new.png'))
                elif item.status == 'in progress':
                    list_item.setIcon(QtGui.QIcon('../graphics/list/balls/started.png'))
                elif item.status == 'paused':
                    list_item.setIcon(QtGui.QIcon('../graphics/list/balls/paused.png'))
                else:
                    print "Unrecognized issue status ({})".format(item.status)

        if ditz_id:
            self.show_item(ditz_id)

    def iterate_all_items(self):
        """
        A lazy generator for iterating all items in the list
        """
        for i in range(self.listWidgetDitzItems.count()):
            yield self.listWidgetDitzItems.item(i)

    def show_item(self, ditz_id=None):
        if not ditz_id or isinstance(ditz_id, QModelIndex):
            # needed so the same function can be connected to GUI
            ditz_id = self._get_selected_issue_id()

        ditz_item = self.ditz.get_issue_content(ditz_id)
        if ditz_item:
            self.textEditDitzItem.setText(str(ditz_item))

        self.enable_valid_actions()

    def comment_issue(self):
        ditz_id = self._get_selected_issue_id()
        if ditz_id == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return
        try:
            dialog = CommentDialog(self.ditz, ditz_id, save=True)
            dialog.ask_comment()
        except DitzError, e:
            QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
            return
        self.show_item() # to reload item data to include the added comment

    def add_reference(self):
        ditz_id = self._get_selected_issue_id()
        if ditz_id == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return
        try:
            dialog = ReferenceDialog(self.ditz, ditz_id)
            dialog.ask_reference()
        except DitzError, e:
            QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
            return
        self.show_item() # to reload item data to include the added comment

    def new_issue(self):
        try:
            dialog = IssueDialog(self.ditz)
            dialog.ask_new_issue()
        except DitzError, e:
            QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
            return
        self.reload_data()

    def edit_issue(self):
        ditz_id = self._get_selected_issue_id()
        if ditz_id == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return
        try:
            dialog = IssueDialog(self.ditz)
            dialog.ask_edit_issue(ditz_id)
        except DitzError, e:
            QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
            return
        self.reload_data()

    def close_issue(self):
        ditz_id = self._get_selected_issue_id()
        if ditz_id != None:
            dialog = CloseDialog(self.ditz, ditz_id)
            dialog.ask_issue_close()
            self.reload_data()
        else:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return

    def drop_issue(self):
        ditz_id = self._get_selected_issue_id()
        if ditz_id == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return
        try:
            self.ditz.drop_issue(ditz_id)
        except DitzError, e:
            QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
            return
        self.reload_data(ditz_id)

    def assign_issue(self):
        ditz_id = self._get_selected_issue_id()
        if ditz_id == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return
        try:
            dialog = AssignDialog(self.ditz)
            dialog.ask_assign_issue(ditz_id)
        except DitzError, e:
            QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
            return
        self.reload_data()

    def start_work(self):
        ditz_id = self._get_selected_issue_id()
        if ditz_id == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return
        dialog = CommentDialog(self.ditz, ditz_id)
        comment = dialog.ask_comment()
        if comment != None:
            try:
                self.ditz.start_work(ditz_id, comment)
            except DitzError, e:
                QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
                return
            self.reload_data(ditz_id)

    def stop_work(self):
        ditz_id = self._get_selected_issue_id()
        if ditz_id == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return
        dialog = CommentDialog(self.ditz, ditz_id)
        comment = dialog.ask_comment()
        if comment != None:
            try:
                self.ditz.stop_work(ditz_id, comment)
            except DitzError, e:
                QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
                return
            self.reload_data(ditz_id)

    def make_release(self):
        ditz_id = self._get_selected_issue_id()
        if ditz_id == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No item selected")
            return
        release_name = self._get_selected_release_name()
        if release_name == None:
            return
        dialog = CommentDialog(self.ditz, None)
        comment = dialog.ask_comment()
        if comment != None:
            self.ditz.make_release(release_name, comment)
            self.reload_data()

    def open_settings(self):
        try:
            dialog = SettingsDialog(self.config)
            dialog.show_settings()
        except DitzError, e:
            QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
            return
        self.reload_data()

    def quit_application(self):
        QtGui.qApp.quit()

    def _get_selected_issue_id(self):
        item_type = self._get_selected_item_type()
        if item_type != "issue":
            return None
        text = self._get_selected_item_text()
        if not text:
            return None
        ditz_id = text.split(' ', 1)[0]
        return ditz_id

    def _get_selected_issue_status(self):
        text = self._get_selected_item_text()
        if not text:
            return None
        return self._get_issue_status(text)

    def _get_selected_release_name(self):
        text = self._get_selected_item_text()
        if not text:
            return None
        release_name = text.split()[0]
        if release_name not in self.ditz.get_releases():
            return None
        return release_name

    def _get_selected_item_type(self):
        text = self._get_selected_item_text()
        if not text:
            return None
        return self._get_item_type(text)

    def _get_selected_item_text(self):
        item = self.listWidgetDitzItems.currentItem()
        if not item:
            return None
        text = str(item.text())
        if len(text) == 0:
            return None
        return text

    def _get_issue_status(self, item_text):
        if not item_text:
            return None
        ditz_id = item_text.split(' ', 1)[0]
        item_status = self.ditz.get_issue_status_by_ditz_id(ditz_id)
        return item_status

    def _get_item_type(self, item_text):
        ditz_id = item_text.split(' ', 1)[0]
        item = self.ditz.get_issue_from_cache(ditz_id)
        if item != None:
            return item.item_type
        return None

def main():
    app = QtGui.QApplication(sys.argv)
    _ = DitzGui()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
