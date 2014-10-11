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
from PyQt4.QtCore import SIGNAL, QModelIndex, QSize

from ditzcontrol import DitzControl
from comment_dialog import CommentDialog
from close_dialog import CloseDialog

class DitzGui(QtGui.QMainWindow):
    """
    The main window
    """
    def __init__(self):
        """
        Initialize user interface
        """
        super(DitzGui, self).__init__()

        self.ditzControl = DitzControl()

        uic.loadUi('../ui/main_window.ui', self)

        self.reload_data()

        self.connect(self.listWidgetDitzItems,
                SIGNAL('customContextMenuRequested(const QPoint &)'),
                self.context_menu)

        self.actionReload.triggered.connect(self.reload_data)
        self.actionExit.triggered.connect(self.quit_application)
        self.listWidgetDitzItems.clicked.connect(self.show_item)

        self.toolbar_menu_actions()

        self.resize(800, 500)
        self.center()
        self.setWindowTitle('Ditz GUI')
        self.setWindowIcon(QtGui.QIcon('../graphics/ditz_gui_icon.png'))
        self.show()

    def center(self):
        """
        Center the window to screen
        """
        rect = self.frameGeometry()
        desktop_center = QtGui.QDesktopWidget().availableGeometry().center()
        rect.moveCenter(desktop_center)
        self.move(rect.topLeft())

    def context_menu(self):
        ditz_id = self._get_selected_item_id()
        status = self._get_selected_item_status()
        menu = QtGui.QMenu(self)
        menu.addAction("New issue")
        menu.addAction("Comment " + ditz_id, lambda:self.comment(ditz_id))
        if status != "started":
            menu.addAction("Start work on " + ditz_id, lambda:self.start_work(ditz_id))
        else:
            menu.addAction("Stop work on " + ditz_id, lambda:self.stop_work(ditz_id))
        menu.addAction("Close " + ditz_id, lambda:self.close_issue(ditz_id))
        menu.addAction("Drop " + ditz_id)
        menu.exec_(QtGui.QCursor.pos())

    def toolbar_menu_actions(self):
        ditz_id = self._get_selected_item_id()
        status = self._get_selected_item_status()

        #self.toolBar.setIconSize(QSize(32,32))
        action_new_issue = QtGui.QAction(QtGui.QIcon('../graphics/new.png'), 'New Issue', self)
        action_comment_issue = QtGui.QAction(QtGui.QIcon('../graphics/comment.png'), 'Comment Issue', self)
        action_start_work = QtGui.QAction(QtGui.QIcon('../graphics/start.png'), 'Start working', self)
        action_stop_work = QtGui.QAction(QtGui.QIcon('../graphics/stop.png'), 'Stop working', self)
        action_close_issue = QtGui.QAction(QtGui.QIcon('../graphics/close.png'), 'Close issue', self)
        action_drop_issue = QtGui.QAction(QtGui.QIcon('../graphics/drop.png'), 'Drop issue', self)

        action_close_issue.triggered.connect(self.make_release) #TODO: just to try

        self.toolBar.addAction(action_new_issue)
        self.toolBar.addAction(action_comment_issue)
        self.toolBar.addAction(action_start_work)
        self.toolBar.addAction(action_stop_work)
        self.toolBar.addAction(action_close_issue)
        self.toolBar.addAction(action_drop_issue)

    def reload_data(self, ditz_id=None):
        data = self.ditzControl.get_items()
        self.listWidgetDitzItems.clear()
        for item in data:
            self.listWidgetDitzItems.addItem(item)
        if ditz_id:
            self.show_item(ditz_id)

        #TODO: set cool icons and/or formatting based on item being release or issue?
        #TODO: or releases and issues should be organized differently already in ditzcontrol?
        for item in self.iterate_all_items():
            item_text = str(item.text())
            if len(item_text) == 0:
                continue
            item_type = self._get_item_type(item_text)
            if item_type == 'issue':
                item_status = self._get_item_status(item_text)
                if item_status == 'new':
                    item.setIcon(QtGui.QIcon('../graphics/new.png'))
                elif item_status == 'started':
                    item.setIcon(QtGui.QIcon('../graphics/start.png'))
                elif item_status == 'paused':
                    item.setIcon(QtGui.QIcon('../graphics/pause.png'))
            #elif item_type == 'release':
            #    item.setIcon(QtGui.QIcon('../graphics/close.png'))

    def iterate_all_items(self):
        for i in range(self.listWidgetDitzItems.count()):
            yield self.listWidgetDitzItems.item(i)

    def show_item(self, ditz_id=None):
        if not ditz_id or isinstance(ditz_id, QModelIndex):
            # needed so the same function can be connected to GUI
            ditz_id = self._get_selected_item_id()
        item = self.ditzControl.get_item(ditz_id)
        if item:
            self.textEditDitzItem.setText(str(item))
        #TODO: format the data or use a form

    def comment(self, ditz_id):
        dialog = CommentDialog(ditz_id, save=True)
        dialog.askComment()
        self.show_item() # to reload item data to include the added comment

    def close_issue(self, ditz_id):
        dialog = CloseDialog(ditz_id)
        dialog.askIssueClose()
        self.reload_data()

    def start_work(self, ditz_id):
        dialog = CommentDialog(ditz_id)
        comment = dialog.askComment()
        if comment != None:
            self.ditzControl.start_work(ditz_id, comment)
            self.reload_data(ditz_id)

    def stop_work(self, ditz_id):
        dialog = CommentDialog(ditz_id)
        comment = dialog.askComment()
        if comment != None:
            self.ditzControl.stop_work(ditz_id, comment)
            self.reload_data(ditz_id)

    def make_release(self, release_name):
        release_name = self._get_selected_release_name()
        if release_name == None:
            return
        dialog = CommentDialog(None)
        comment = dialog.askComment()
        if comment != None:
            self.ditzControl.make_release(release_name, comment)
            self.reload_data()

    def quit_application(self):
        QtGui.qApp.quit()

    def _get_selected_item_id(self):
        text = self._get_selected_item_text()
        if not text:
            return None
        item_type = self._get_selected_item_type()
        if item_type != "issue":
            return None
        ditz_id = text.split()[1][:-1]
        return ditz_id

    def _get_selected_item_status(self):
        text = self._get_selected_item_text()
        if not text:
            return None
        return self._get_item_status(text)

    def _get_selected_release_name(self):
        text = self._get_selected_item_text()
        if not text:
            return None
        release_name = text.split()[0]
        if release_name not in self.ditzControl.get_releases():
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

    def _get_item_status(self, item_text):
        status_identifier = item_text.split()[0][:1]
        return self.ditzControl.status_identifier_to_string(status_identifier)

    def _get_item_type(self, item_text):
        if self.ditzControl.status_identifier_to_string(item_text.split()[0][:1]) != None:
            return "issue"
        if item_text.split()[0] in self.ditzControl.get_releases():
            return "release"
        return None

def main():
    app = QtGui.QApplication(sys.argv)
    ditz_gui = DitzGui()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
