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

from common.items import DitzRelease, DitzIssue
from common.errors import DitzError
from common.unused import unused
from config import ConfigControl
from ditzcontrol import DitzControl
from comment_dialog import CommentDialog
from reference_dialog import ReferenceDialog
from issue_dialog import IssueDialog
from close_dialog import CloseDialog
from settings_dialog import SettingsDialog
from assign_dialog import AssignDialog
from release_dialog import ReleaseDialog

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
        self.config.load_configs()
        self.ditz = DitzControl(self.config)

        uic.loadUi('../ui/main_window.ui', self)

        self.reload_data()

        self.actionCommentIssue = None
        self.actionStartWork = None
        self.actionStopWork = None
        self.actionAddReference = None
        self.actionEditIssue = None
        self.actionNewIssue = None
        self.actionCloseIssue = None
        self.actionDropIssue = None
        self.actionAssignIssue = None

        self.actionNewRelease = None
        self.actionEditRelease = None
        self.actionMakeRelease = None
        self.actionRemoveRelease = None

        self.actionOpenSettings = None

        self.create_actions()
        self.connect_actions()
        self.add_action_shortcuts()
        self.build_toolbar_menu()
        self.enable_valid_actions()

        self.show_main_window()

    def show_main_window(self):
        """
        Show the main application window
        """
        window_size = self.config.get_app_configs().window_size
        self.resize(window_size[0], window_size[1])
        self.center()
        self.setWindowTitle('Ditz GUI')
        self.setWindowIcon(QtGui.QIcon('../graphics/ditz_gui_icon.png'))
        self.show()

    def create_actions(self):
        """
        Create action objects
        """
        self.actionNewIssue = QtGui.QAction(QtGui.QIcon('../graphics/issue/new.png'), 'New Issue', self)
        self.actionEditIssue = QtGui.QAction(QtGui.QIcon('../graphics/issue/edit.png'), 'Edit Issue', self)
        self.actionCommentIssue = QtGui.QAction(QtGui.QIcon('../graphics/issue/comment.png'), 'Comment Issue', self)
        self.actionStartWork = QtGui.QAction(QtGui.QIcon('../graphics/issue/start.png'), 'Start working', self)
        self.actionStopWork = QtGui.QAction(QtGui.QIcon('../graphics/issue/stop.png'), 'Stop working', self)
        self.actionCloseIssue = QtGui.QAction(QtGui.QIcon('../graphics/issue/close.png'), 'Close issue', self)
        self.actionDropIssue = QtGui.QAction(QtGui.QIcon('../graphics/issue/drop.png'), 'Drop issue', self)
        self.actionAssignIssue = QtGui.QAction(QtGui.QIcon('../graphics/issue/assign.png'),
                'Assign Issue to a release', self)
        self.actionAddReference = QtGui.QAction(QtGui.QIcon('../graphics/issue/add_reference.png'),
                'Add reference', self)

        self.actionNewRelease = QtGui.QAction(QtGui.QIcon('../graphics/release/new_release.png'),
               'Add release', self)
        self.actionEditRelease = QtGui.QAction(QtGui.QIcon('../graphics/release/edit_release.png'),
               'Edit release', self)
        self.actionMakeRelease = QtGui.QAction(QtGui.QIcon('../graphics/release/make_release.png'),
                'Make release', self)
        self.actionRemoveRelease = QtGui.QAction(QtGui.QIcon('../graphics/release/remove_release.png'),
                'Remove release', self)

        self.actionOpenSettings = QtGui.QAction(QtGui.QIcon('../graphics/misc/settings.png'), 'Settings', self)

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

        self.actionNewRelease.iconVisibleInMenu = True
        self.actionEditRelease.iconVisibleInMenu = True
        self.actionMakeRelease.iconVisibleInMenu = True
        self.actionRemoveRelease.iconVisibleInMenu = True
        self.actionOpenSettings.iconVisibleInMenu = True

    def connect_actions(self):
        """
        Connect actions to slots
        """
        # issue related actions
        self.actionNewIssue.triggered.connect(self.new_issue)
        self.actionEditIssue.triggered.connect(self.edit_issue)
        self.actionCommentIssue.triggered.connect(self.comment_issue)
        self.actionStartWork.triggered.connect(self.start_work)
        self.actionStopWork.triggered.connect(self.stop_work)
        self.actionCloseIssue.triggered.connect(self.close_issue)
        self.actionDropIssue.triggered.connect(self.drop_issue)
        self.actionAssignIssue.triggered.connect(self.assign_issue)
        self.actionAddReference.triggered.connect(self.add_reference)

        # release related actions
        self.actionNewRelease.triggered.connect(self.new_release)
        self.actionEditRelease.triggered.connect(self.edit_release)
        self.actionMakeRelease.triggered.connect(self.make_release)
        self.actionRemoveRelease.triggered.connect(self.remove_release)

        # common actions
        self.actionOpenSettings.triggered.connect(self.open_settings)

        # connect qt creator created actions
        self.actionReload.triggered.connect(self.reload_data)
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionExit.triggered.connect(self.quit_application)

        # main listwidget actions
        self.listWidgetDitzItems.clicked.connect(self.show_item)
        self.connect(self.listWidgetDitzItems,
                SIGNAL('customContextMenuRequested(const QPoint &)'),
                self.context_menu)
        self.connect(self.listWidgetDitzItems,
                SIGNAL("itemSelectionChanged()"),
                self.show_item)

    def add_action_shortcuts(self):
        """
        Simple shortcuts for common actions to make the software usable
        using only a keyboard.
        """
        self.actionNewIssue.setShortcut('N')
        self.actionEditIssue.setShortcut('E')
        self.actionCommentIssue.setShortcut('C')
        self.actionStartWork.setShortcut('S')
        self.actionStopWork.setShortcut('S')
        self.actionCloseIssue.setShortcut('L')
        self.actionDropIssue.setShortcut('D')
        self.actionAssignIssue.setShortcut('A')
        self.actionAddReference.setShortcut('R')

    def enable_valid_actions(self):
        """
        Enabled (toolbar) actions that are valid at the moment.
        Only common actions and actions valid for an item currently selected
        should be enabled. Others are disabled.
        """
        issue = self._get_selected_issue()
        release = self._get_selected_release_name()
        if issue:
            if issue.status == 'in progress':
                start_state = False
            else:
                start_state = True
            self._set_issue_actions(True, start_state)
            self._set_release_actions(False)
        elif release:
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
        self.actionEditRelease.setEnabled(state)
        self.actionMakeRelease.setEnabled(state)
        self.actionRemoveRelease.setEnabled(state)

    def center(self):
        """
        Center the window to screen
        """
        rect = self.frameGeometry()
        desktop_center = QtGui.QDesktopWidget().availableGeometry().center()
        rect.moveCenter(desktop_center)
        self.move(rect.topLeft())

    def update_action_texts(self):
        issue = self._get_selected_issue()
        release = self._get_selected_release_name()

        if issue:
            self.actionEditIssue.setText('Edit ' + issue.name)
            self.actionCommentIssue.setText('Comment ' + issue.name)
            self.actionStartWork.setText('Start working on ' + issue.name)
            self.actionStopWork.setText('Stop work on ' + issue.name)
            self.actionCloseIssue.setText('Close ' + issue.name)
            self.actionDropIssue.setText('Drop ' + issue.name)
            self.actionAssignIssue.setText('Assign issue ' + issue.name + ' to a release')
            self.actionAddReference.setText('Add reference to ' + issue.name)
        else:
            self.actionEditIssue.setText('Edit issue')
            self.actionCommentIssue.setText('Comment issue')
            self.actionStartWork.setText('Start working')
            self.actionStopWork.setText('Stop working')
            self.actionCloseIssue.setText('Close issue')
            self.actionDropIssue.setText('Drop issue')
            self.actionAssignIssue.setText('Assign issue to a release')
            self.actionAddReference.setText('Add reference')

    def context_menu(self):
        # pylint: disable=W0108
        self.show_item() # to reload item data first

        issue = self._get_selected_issue()
        release = self._get_selected_release_name()
        menu = QtGui.QMenu(self)

        if issue:
            self.update_action_texts()

            menu.addAction(self.actionNewIssue)
            menu.addAction(self.actionEditIssue)
            menu.addAction(self.actionCommentIssue)
            menu.addAction(self.actionAddReference)
            if issue.status != "in progress" and issue.status != "started":
                menu.addAction(self.actionStartWork)
            else:
                menu.addAction(self.actionStopWork)
            menu.addAction(self.actionCloseIssue)
            menu.addAction(self.actionDropIssue)
            menu.addAction(self.actionAssignIssue)
            menu.addAction(self.actionNewRelease)
        elif release:
            menu.addAction(self.actionNewIssue)
            menu.addAction(self.actionNewRelease)
            menu.addAction(self.actionEditRelease)
            menu.addAction(self.actionMakeRelease)
            menu.addAction(self.actionRemoveRelease)
            #TODO: add issue directly to this release?
        else:
            # empty lines
            menu.addAction(self.actionNewIssue)

        menu.exec_(QtGui.QCursor.pos())

    def build_toolbar_menu(self):
        # issue actions
        self.toolBar.addAction(self.actionNewIssue)
        self.toolBar.addAction(self.actionEditIssue)
        self.toolBar.addAction(self.actionCommentIssue)
        self.toolBar.addAction(self.actionStartWork)
        self.toolBar.addAction(self.actionStopWork)
        self.toolBar.addAction(self.actionCloseIssue)
        self.toolBar.addAction(self.actionDropIssue)

        # spacer
        spacer = QtGui.QWidget()
        size = self.toolBar.iconSize()
        spacer.setFixedSize(size.width(), size.height())
        self.toolBar.addWidget(spacer)

        # release actions
        self.toolBar.addAction(self.actionNewRelease)
        self.toolBar.addAction(self.actionEditRelease)
        self.toolBar.addAction(self.actionMakeRelease)
        self.toolBar.addAction(self.actionRemoveRelease)

        # spacer
        wide_spacer = QtGui.QWidget()
        wide_spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        self.toolBar.addWidget(wide_spacer)

        # other common actions
        self.toolBar.addAction(self.actionOpenSettings)

    def reload_data(self, ditz_id=None):
        data = self.ditz.get_items()
        self.listWidgetDitzItems.clear()
        for item in data:
            if isinstance(item, DitzRelease) and self.listWidgetDitzItems.count() > 0:
                # add one empty line as a spacer (except on the first line)
                self.listWidgetDitzItems.addItem("")
            if item.name == None:
                title = item.title
            else:
                title = "{:<13}{}".format(item.name, item.title)  #TODO: hardcoded column width
            self.listWidgetDitzItems.addItem(title)

            # set icon to the added item
            list_item = self.listWidgetDitzItems.item(self.listWidgetDitzItems.count() - 1)
            if isinstance(item, DitzIssue):
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
            ditz_item = self._get_selected_issue()
        else:
            ditz_item = self.ditz.get_issue_content(ditz_id)
        if ditz_item:
            self.textEditDitzItem.setHtml(ditz_item.toHtml())
        else:
            release_name = self._get_selected_release_name()
            if release_name:
                release = self.ditz.get_release_from_cache(release_name)
                if release:
                    self.textEditDitzItem.setHtml(release.toHtml())
                else:
                    self.textEditDitzItem.setHtml("Release not found")
            else:
                self.textEditDitzItem.setHtml("")

        self.enable_valid_actions()
        self.update_action_texts()

    def comment_issue(self):
        issue = self._get_selected_issue()
        if issue == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return
        try:
            dialog = CommentDialog(self.ditz, issue.identifier, save=True)
            dialog.ask_comment()
        except DitzError, e:
            QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
            return
        self.show_item() # to reload item data to include the added comment

    def add_reference(self):
        issue = self._get_selected_issue()
        if issue == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return
        try:
            dialog = ReferenceDialog(self.ditz, issue.identifier)
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
        issue = self._get_selected_issue()
        if issue == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return
        try:
            dialog = IssueDialog(self.ditz)
            dialog.ask_edit_issue(issue.identifier)
        except DitzError, e:
            QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
            return
        self.reload_data()

    def close_issue(self):
        issue = self._get_selected_issue()
        if issue != None:
            dialog = CloseDialog(self.ditz, issue.identifier)
            dialog.ask_issue_close()
            self.reload_data()
        else:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return

    def drop_issue(self):
        issue = self._get_selected_issue()
        if issue == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return
        try:
            self.ditz.drop_issue(issue.identifier)
        except DitzError, e:
            QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
            return
        self.reload_data(issue.identifier)

    def assign_issue(self):
        issue = self._get_selected_issue()
        if issue == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return
        try:
            dialog = AssignDialog(self.ditz)
            dialog.ask_assign_issue(issue.identifier)
        except DitzError, e:
            QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
            return
        self.reload_data()

    def start_work(self):
        issue = self._get_selected_issue()
        if issue == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return

        title = 'Start work on {}'.format(issue.name)
        dialog = CommentDialog(self.ditz, issue.identifier, title=title)
        comment = dialog.ask_comment()
        if comment != None:
            try:
                self.ditz.start_work(issue.identifier, comment)
            except DitzError, e:
                QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
                return
            self.reload_data(issue.identifier)

    def stop_work(self):
        issue = self._get_selected_issue()
        if issue == None:
            QtGui.QMessageBox.warning(self, "ditz-gui error", "No issue selected")
            return
        title = 'Stop work on {}'.format(issue.name)
        dialog = CommentDialog(self.ditz, issue.identifier, title=title)
        comment = dialog.ask_comment()
        if comment != None:
            try:
                self.ditz.stop_work(issue.identifier, comment)
            except DitzError, e:
                QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
                return
            self.reload_data(issue.identifier)

    def new_release(self):
        dialog = ReleaseDialog(self.ditz)
        release = dialog.add_release()
        if release:
            self.reload_data()

    def edit_release(self):
        release_name = self._get_selected_release_name()
        if release_name == None:
            return
        dialog = ReleaseDialog(self.ditz)
        release = dialog.edit_release(release_name)
        if release:
            self.reload_data()

    def make_release(self):
        release_name = self._get_selected_release_name()
        if release_name == None:
            return
        title = 'Release {}'.format(release_name)
        dialog = CommentDialog(self.ditz, None, title=title)
        comment = dialog.ask_comment()
        if comment != None:
            self.ditz.make_release(release_name, comment)
            self.reload_data()

    def remove_release(self):
        #TODO: implementation of removing a release
        pass

    def open_settings(self):
        try:
            dialog = SettingsDialog(self.config)
            dialog.show_settings()
        except DitzError, e:
            QtGui.QMessageBox.warning(self, "Ditz error", e.error_message)
            return
        self.reload_data()

    def closeEvent(self, event):
        unused(event)
        self._save_window_size()

    def quit_application(self):
        self._save_window_size()
        QtGui.qApp.quit()

    def _get_selected_issue_name(self):
        issue = self._get_selected_issue()
        if not issue:
            return None
        return issue.name

    def _save_window_size(self):
        """
        Application is about to be closed. Save window size, if the setting is enabled.
        """
        settings = self.config.get_app_configs()
        if settings.remember_window_size == True:
            width = self.geometry().width()
            height = self.geometry().height()
            settings.window_size = [width, height]
            self.config.appconfig.write_config_file()

    def _get_selected_issue_status(self):
        text = self._get_selected_item_text()
        if not text:
            return None
        return self._get_issue_status(text)

    def _get_selected_release_name(self):
        text = self._get_selected_item_text()
        if not text or text == '':
            return None
        columns = text.split()
        if len(columns) < 2:
            return None
        if columns[1] not in self.ditz.config.get_releases('unreleased', True):
            return None
        return columns[1]

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

    def _get_selected_issue(self):
        item_text = self._get_selected_item_text()
        if not item_text:
            return None
        ditz_id = item_text.split(' ', 1)[0]
        item = self.ditz.get_issue_from_cache(ditz_id)
        return item


def main():
    app = QtGui.QApplication(sys.argv)
    _ = DitzGui()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
