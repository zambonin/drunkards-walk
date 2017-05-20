#!/usr/bin/env python

from math import cos, sin
from PyQt5.QtCore import QThread, pyqtSignal
from random import randint


class MonteCarloSim(QThread):

    prr_signal, pri_signal = pyqtSignal(int), pyqtSignal(int)
    plt_signal = pyqtSignal(list, list, list, list, list)

    def __init__(self, replications, iterations):
        super().__init__()
        self.replications = replications
        self.iterations = iterations

    def __del__(self):
        self.wait()

    def run(self):
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
