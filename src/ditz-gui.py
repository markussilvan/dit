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
from common.errors import DitzError, ApplicationError
from common.unused import unused
from config import ConfigControl, MOVE_UP, MOVE_DOWN
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

        try:
            self.config = ConfigControl()
        except ApplicationError, e:
            message = "{}.\n{}\n{}".format(e.error_message,
                    "Run 'ditz init' first to initialize or",
                    "start Ditz GUI in any subdirectory of\nan initialized Ditz project.")
            QtGui.QMessageBox.warning(self, "Ditz not initialized", message)
            sys.exit(1)

        try:
            self.config.load_configs()
        except ApplicationError, e:
            if e.error_message == "Ditz config not found":
                message = "{}\n{}".format(e.error_message,
                        "Go to settings to configure before using")
                QtGui.QMessageBox.warning(self, "Configuration error", e.error_message)
            elif e.error_message == "Project file not found":
                QtGui.QMessageBox.warning(self, "Fatal configuration error", e.error_message)
                sys.exit(1)
            else:
                print e.error_message
                sys.exit(1)

        self.ditz = DitzControl(self.config)

        uic.loadUi('../ui/main_window.ui', self)

        self.reload_data()

        self.actions = {}

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
        self.actions['new_issue'] = QtGui.QAction(QtGui.QIcon('../graphics/issue/new.png'),
                'New Issue', self)
        self.actions['edit_issue'] = QtGui.QAction(QtGui.QIcon('../graphics/issue/edit.png'),
                'Edit Issue', self)
        self.actions['comment_issue'] = QtGui.QAction(QtGui.QIcon('../graphics/issue/comment.png'),
                'Comment Issue', self)
        self.actions['start_work'] = QtGui.QAction(QtGui.QIcon('../graphics/issue/start.png'),
                'Start working', self)
        self.actions['stop_work'] = QtGui.QAction(QtGui.QIcon('../graphics/issue/stop.png'),
                'Stop working', self)
        self.actions['close_issue'] = QtGui.QAction(QtGui.QIcon('../graphics/issue/close.png'),
                'Close issue', self)
        self.actions['drop_issue'] = QtGui.QAction(QtGui.QIcon('../graphics/issue/drop.png'),
                'Drop issue', self)
        self.actions['assign_issue'] = QtGui.QAction(QtGui.QIcon('../graphics/issue/assign.png'),
                'Assign Issue to a release', self)
        self.actions['add_reference'] = QtGui.QAction(
                QtGui.QIcon('../graphics/issue/add_reference.png'), 'Add reference', self)

        self.actions['new_release'] = QtGui.QAction(
                QtGui.QIcon('../graphics/release/new_release.png'), 'Add release', self)
        self.actions['edit_release'] = QtGui.QAction(
                QtGui.QIcon('../graphics/release/edit_release.png'), 'Edit release', self)
        self.actions['make_release'] = QtGui.QAction(
                QtGui.QIcon('../graphics/release/make_release.png'), 'Make release', self)
        self.actions['remove_release'] = QtGui.QAction(
                QtGui.QIcon('../graphics/release/remove_release.png'), 'Remove release', self)
        self.actions['move_up_release'] = QtGui.QAction(
                QtGui.QIcon('../graphics/release/move_up_release.png'), 'Move release up', self)
        self.actions['move_down_release'] = QtGui.QAction(
                QtGui.QIcon('../graphics/release/move_down_release.png'), 'Move release down', self)

        self.actions['open_settings'] = QtGui.QAction(
                QtGui.QIcon('../graphics/misc/settings.png'), 'Settings', self)

        # icons visible in custom context menu of items list view
        self.actions['new_issue'].iconVisibleInMenu = True
        self.actions['edit_issue'].iconVisibleInMenu = True
        self.actions['comment_issue'].iconVisibleInMenu = True
        self.actions['start_work'].iconVisibleInMenu = True
        self.actions['stop_work'].iconVisibleInMenu = True
        self.actions['close_issue'].iconVisibleInMenu = True
        self.actions['drop_issue'].iconVisibleInMenu = True
        self.actions['assign_issue'].iconVisibleInMenu = True
        self.actions['add_reference'].iconVisibleInMenu = True

        self.actions['new_release'].iconVisibleInMenu = True
        self.actions['edit_release'].iconVisibleInMenu = True
        self.actions['make_release'].iconVisibleInMenu = True
        self.actions['remove_release'].iconVisibleInMenu = True
        self.actions['move_up_release'].iconVisibleInMenu = True
        self.actions['move_down_release'].iconVisibleInMenu = True

        self.actions['open_settings'].iconVisibleInMenu = True

    def connect_actions(self):
        """
        Connect actions to slots
        """
        # issue related actions
        self.actions['new_issue'].triggered.connect(self.new_issue)
        self.actions['edit_issue'].triggered.connect(self.edit_issue)
        self.actions['comment_issue'].triggered.connect(self.comment_issue)
        self.actions['start_work'].triggered.connect(self.start_work)
        self.actions['stop_work'].triggered.connect(self.stop_work)
        self.actions['close_issue'].triggered.connect(self.close_issue)
        self.actions['drop_issue'].triggered.connect(self.drop_issue)
        self.actions['assign_issue'].triggered.connect(self.assign_issue)
        self.actions['add_reference'].triggered.connect(self.add_reference)

        # release related actions
        self.actions['new_release'].triggered.connect(self.new_release)
        self.actions['edit_release'].triggered.connect(self.edit_release)
        self.actions['make_release'].triggered.connect(self.make_release)
        self.actions['remove_release'].triggered.connect(self.remove_release)
        self.actions['move_up_release'].triggered.connect(self.move_release)
        self.actions['move_down_release'].triggered.connect(lambda: self.move_release(MOVE_DOWN))

        # common actions
        self.actions['open_settings'].triggered.connect(self.open_settings)

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
        self.actions['new_issue'].setShortcut('N')
        self.actions['edit_issue'].setShortcut('E')
        self.actions['comment_issue'].setShortcut('C')
        self.actions['start_work'].setShortcut('S')
        self.actions['stop_work'].setShortcut('S')
        self.actions['close_issue'].setShortcut('L')
        self.actions['drop_issue'].setShortcut('D')
        self.actions['assign_issue'].setShortcut('A')
        self.actions['add_reference'].setShortcut('R')

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
        self.actions['edit_issue'].setEnabled(state)
        self.actions['comment_issue'].setEnabled(state)
        if state == True:
            self.actions['start_work'].setEnabled(start_state)
            self.actions['stop_work'].setEnabled(not start_state)
        else:
            self.actions['start_work'].setEnabled(state)
            self.actions['stop_work'].setEnabled(state)
        self.actions['close_issue'].setEnabled(state)
        self.actions['drop_issue'].setEnabled(state)
        self.actions['assign_issue'].setEnabled(state)
        self.actions['add_reference'].setEnabled(state)

    def _set_release_actions(self, state):
        self.actions['edit_release'].setEnabled(state)
        self.actions['make_release'].setEnabled(state)
        self.actions['remove_release'].setEnabled(state)
        self.actions['move_up_release'].setEnabled(state)
        self.actions['move_down_release'].setEnabled(state)

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
            self.actions['edit_issue'].setText('Edit ' + issue.name)
            self.actions['comment_issue'].setText('Comment ' + issue.name)
            self.actions['start_work'].setText('Start working on ' + issue.name)
            self.actions['stop_work'].setText('Stop work on ' + issue.name)
            self.actions['close_issue'].setText('Close ' + issue.name)
            self.actions['drop_issue'].setText('Drop ' + issue.name)
            self.actions['assign_issue'].setText('Assign issue ' + issue.name + ' to a release')
            self.actions['add_reference'].setText('Add reference to ' + issue.name)
        else:
            self.actions['edit_issue'].setText('Edit issue')
            self.actions['comment_issue'].setText('Comment issue')
            self.actions['start_work'].setText('Start working')
            self.actions['stop_work'].setText('Stop working')
            self.actions['close_issue'].setText('Close issue')
            self.actions['drop_issue'].setText('Drop issue')
            self.actions['assign_issue'].setText('Assign issue to a release')
            self.actions['add_reference'].setText('Add reference')

        if release and release != "":
            self.actions['edit_release'].setText('Edit release ' + release)
            self.actions['make_release'].setText('Release ' + release)
            self.actions['remove_release'].setText('Remove release ' + release)
            self.actions['move_up_release'].setText('Move up ' + release)
            self.actions['move_down_release'].setText('Move down ' + release)
        else:
            self.actions['edit_release'].setText('Edit release')
            self.actions['make_release'].setText('Make release')
            self.actions['remove_release'].setText('Remove release')
            self.actions['move_up_release'].setText('Move release up')
            self.actions['move_down_release'].setText('Move release down')

    def context_menu(self):
        # pylint: disable=W0108
        self.show_item() # to reload item data first

        issue = self._get_selected_issue()
        release = self._get_selected_release_name()
        menu = QtGui.QMenu(self)

        if issue:
            self.update_action_texts()

            menu.addAction(self.actions['new_issue'])
            menu.addAction(self.actions['edit_issue'])
            menu.addAction(self.actions['comment_issue'])
            menu.addAction(self.actions['add_reference'])
            if issue.status != "in progress" and issue.status != "started":
                menu.addAction(self.actions['start_work'])
            else:
                menu.addAction(self.actions['stop_work'])
            menu.addAction(self.actions['close_issue'])
            menu.addAction(self.actions['drop_issue'])
            menu.addAction(self.actions['assign_issue'])
            menu.addAction(self.actions['new_release'])
        elif release:
            menu.addAction(self.actions['new_issue'])
            menu.addAction(self.actions['new_release'])
            menu.addAction(self.actions['edit_release'])
            menu.addAction(self.actions['make_release'])
            menu.addAction(self.actions['remove_release'])
            menu.addAction(self.actions['move_up_release'])
            menu.addAction(self.actions['move_down_release'])
        else:
            # empty line selected
            menu.addAction(self.actions['new_issue'])

        menu.exec_(QtGui.QCursor.pos())

    def build_toolbar_menu(self):
        # issue actions
        self.toolBar.addAction(self.actions['new_issue'])
        self.toolBar.addAction(self.actions['edit_issue'])
        self.toolBar.addAction(self.actions['comment_issue'])
        self.toolBar.addAction(self.actions['start_work'])
        self.toolBar.addAction(self.actions['stop_work'])
        self.toolBar.addAction(self.actions['close_issue'])
        self.toolBar.addAction(self.actions['drop_issue'])

        # spacer
        spacer = QtGui.QWidget()
        size = self.toolBar.iconSize()
        spacer.setFixedSize(size.width(), size.height())
        self.toolBar.addWidget(spacer)

        # release actions
        self.toolBar.addAction(self.actions['new_release'])
        self.toolBar.addAction(self.actions['edit_release'])
        self.toolBar.addAction(self.actions['make_release'])
        self.toolBar.addAction(self.actions['remove_release'])
        self.toolBar.addAction(self.actions['move_up_release'])
        self.toolBar.addAction(self.actions['move_down_release'])

        # spacer
        wide_spacer = QtGui.QWidget()
        wide_spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        self.toolBar.addWidget(wide_spacer)

        # other common actions
        self.toolBar.addAction(self.actions['open_settings'])

    def reload_data(self, ditz_id=None):
        data = self.ditz.get_items()
        self.listWidgetDitzItems.clear()

        max_name_width = self.ditz.get_issue_name_max_len()

        for item in data:
            if isinstance(item, DitzRelease) and self.listWidgetDitzItems.count() > 0:
                # add one empty line as a spacer (except on the first line)
                self.listWidgetDitzItems.addItem("")
            if item.name == None:
                title = item.title
            else:
                title = "{0:<{1}}{2}".format(item.name, max_name_width + 1, item.title)
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
        if not self.ditz.can_be_released(release_name):
            error = "Release '{}' can't be released.\nRelease has open tasks.".format(release_name)
            QtGui.QMessageBox.warning(self, "Ditz error", error)
            return
        title = 'Release {}'.format(release_name)
        dialog = CommentDialog(self.ditz, None, title=title)
        comment = dialog.ask_comment()
        if comment != None:
            settings = self.config.get_ditz_configs()
            creator = '{} <{}>'.format(settings.name, settings.email)
            release = self.ditz.get_release_from_cache(release_name)
            release.add_log_entry(None, 'released', creator, comment)
            self.config.projectconfig.make_release(release)
            self.config.projectconfig.write_config_file()
            self.reload_data()

    def remove_release(self):
        release_name = self._get_selected_release_name()
        if release_name == None:
            return
        if self.config.projectconfig.remove_release(release_name) == False:
            error = "Error removing release '{}' from project".format(release_name)
            QtGui.QMessageBox.warning(self, "Ditz error", error)
        else:
            self.config.projectconfig.write_config_file()
            self.reload_data()

    def move_release(self, direction=MOVE_UP):
        release_name = self._get_selected_release_name()
        if release_name == None:
            return
        if self.config.projectconfig.move_release(release_name, direction) == False:
            return
        self.config.projectconfig.write_config_file()
        self.reload_data()

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
