# -*- coding:utf8 -*-
__author__ = 'PyYoshi'

import sys

from PySide import QtGui, QtCore

from Twiq import ui

if '__main__' in __name__:
    p = QtGui.QApplication(sys.argv)
    window = ui.MainWindow()
    window.show()
    sys.exit(p.exec_())