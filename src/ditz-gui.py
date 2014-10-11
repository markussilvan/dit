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
from PyQt4.QtCore import SIGNAL

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
        ditz_id = self.get_selected_item_id()
        menu = QtGui.QMenu(self)
        menu.addAction("New issue")
        menu.addAction("Comment " + ditz_id, lambda:self.comment(ditz_id))
        menu.addAction("Start work on " + ditz_id, lambda:self.start_work(ditz_id))
        menu.addAction("Close " + ditz_id, lambda:self.close_issue(ditz_id))
        menu.addAction("Drop " + ditz_id)
        menu.exec_(QtGui.QCursor.pos())

    def reload_data(self):
        data = self.ditzControl.get_items()
        self.listWidgetDitzItems.clear()
        for item in data:
            self.listWidgetDitzItems.addItem(item)
        #TODO: set cool icons and/or formatting based on item being release or issue?
        #TODO: or releases and issues should be organized differently already in ditzcontrol?

    def show_item(self):
        ditz_id = self.get_selected_item_id()
        item = self.ditzControl.get_item(ditz_id)
        if item != None:
            self.textEditDitzItem.setText(str(item))
        #TODO: format the data

    def comment(self, ditz_id):
        dialog = CommentDialog(ditz_id, save=True)
        dialog.askComment()
        self.show_item(ditz_id) # to reload item data to include the comment

    def close_issue(self, ditz_id):
        dialog = CloseDialog(ditz_id)
        dialog.askIssueClose()
        self.reload_data()

    def start_work(self, ditz_id):
        dialog = CommentDialog(ditz_id)
        comment = dialog.askComment()
        self.ditzControl.start_work(ditz_id, comment)

    def quit_application(self):
        QtGui.qApp.quit()

    def get_selected_item_id(self):
        text = str(self.listWidgetDitzItems.currentItem().text())
        if len(text) == 0:
            return None
        ditz_id = text.split()[1][:-1]
        #TODO: check if its an issue or an release or empty line selected...
        return ditz_id

def main():
    app = QtGui.QApplication(sys.argv)
    ditz_gui = DitzGui()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
