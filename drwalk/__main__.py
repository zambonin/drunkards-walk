#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""__main__.py

The main file for `drwalk`, a Monte Carlo method that simulates random walks
and compares those with the expected distance after a number `n` of steps.

    * `PyQt5.QtWidgets.QApplication` handles the initialization, finalization,
        control flow and main settings for the GUI application.
"""

from PyQt5.QtWidgets import QApplication
from .qt_window import AppWindow
from sys import argv, exit

app = QApplication(argv)
aw = AppWindow()
aw.show()
exit(app.exec_())
