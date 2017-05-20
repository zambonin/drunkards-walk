#!/usr/bin/env python

from PyQt5.QtWidgets import QApplication
from .qt_window import ApplicationWindow
from sys import argv, exit

app = QApplication(argv)
aw = ApplicationWindow()
aw.show()
exit(app.exec_())
