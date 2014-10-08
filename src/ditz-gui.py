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

        self.resize(800, 500)
        self.center()
        self.setWindowTitle('Ditz GUI')
        self.setWindowIcon(QtGui.QIcon('../graphics/ditz_gui_icon.png'))
        self.show()

        #TODO: custom context menus not working!
        self.connect(self, SIGNAL('customContextMenuRequested(const QPoint &)'),
                self.context_menu)
        self.connect(self.listWidget, SIGNAL('customContextMenuRequested(const QPoint &)'),
                self.context_menu)

        self.actionReload.triggered.connect(self.reload_data)
        self.actionExit.triggered.connect(self.quit_application)

    def center(self):
        """
        Center the window to screen
        """
        rect = self.frameGeometry()
        desktop_center = QtGui.QDesktopWidget().availableGeometry().center()
        rect.moveCenter(desktop_center)
        self.move(rect.topLeft())

    def context_menu(self):
        menu = QMenu(self)
        menu.addAction("New issue")
        menu.addAction("Delete ditz-gui-xxx")
        menu.exec_(QCursor.pos())

    def reload_data(self):
        data = self.ditzControl.get_items()
        #TODO: use ditzcontrol to reload data

    def quit_application(self):
        QtGui.qApp.quit()

def main():
    app = QtGui.QApplication(sys.argv)
    ditz_gui = DitzGui()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
