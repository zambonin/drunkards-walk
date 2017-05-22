#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""monte_carlo.py

A number crunching class that simulates the drunken sailor's random walk [1]
in a separate thread.

    * `PyQt5.QtCore.QThread` is a class that provides platform-independent
        management of threads within the program.
    * `PyQt5.QtCore.pyqtSignal` is a class attribute that is bound to a
        class instance whenever it is called, allowing data transfer
        between threads.

[1] http://blog.wolfram.com/2011/06/08/
"""

from math import cos, sin
from PyQt5.QtCore import QThread, pyqtSignal
from random import randint


class MonteCarloSim(QThread):
    """
    A QThread reimplementation that may emit three signals, discussed below:

        prr_signal: progress bar signal for replications (r), an integer
                    emitted every time a replication is calculated.
        pri_signal: progress bar signal for iterations (i), an integer emitted
                    every time an iteration is calculated, but only if
                    the number of replications is trivial. Otherwise, emitting
                    `r` * `i` signals would slow the execution terribly.
        plt_signal: plotting signal, a tuple of lists with the final data:
                    `x` and `y` coordinates for the random points, estimated
                    and walked distances, and their differences.
    """
    prr_signal = pyqtSignal(int)
    pri_signal = pyqtSignal(int)
    plt_signal = pyqtSignal(list, list, list, list, list)

    def __init__(self, replications, iterations):
        """
        Initializes a MonteCarloSim object with the following attributes:

            replications:   number of times the experiment must be repeated.
            iterations:     number of steps taken on the random walk.
        """
        super().__init__()
        self.replications = replications
        self.iterations = iterations

    def run(self):
        """
        The starting point for the thread. Returning from this method will
        end the execution of the thread. Takes the attributes and creates
        lists that will be populated with random data and calculations
        derived from it. Emits signals on every iteration.
        """
        rdis = [0] * self.replications

        for r in range(self.replications):
            xpos, ypos, dist, expt = ([0] * self.iterations for _ in range(4))

            for i in range(self.iterations):
                angle = randint(0, 360)
                xpos[i] = xpos[i - 1] + (i + 1) * cos(angle)
                ypos[i] = ypos[i - 1] + (i + 1) * sin(angle)
                dist[i] = (xpos[i] ** 2 + ypos[i] ** 2) ** .5
                expt[i] = self.iterations * (i ** .5)

                if self.replications == 1:
                    self.pri_signal.emit(i + 1)

            rdis[r] = abs(dist[-1] - expt[-1])
            self.prr_signal.emit(r + 1)

        self.plt_signal.emit(xpos, ypos, dist, expt, rdis)
