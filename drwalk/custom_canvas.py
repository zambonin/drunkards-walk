#!/usr/bin/env python

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as Toolbar
from matplotlib.pyplot import subplots


class CustomCanvas(FCanvas):

    def __init__(self, *data):
        fig, self.axes = subplots()
        self.axes.ticklabel_format(style='sci', scilimits=(0, 0))
        self.data = data
        self.create_figure()
        super().__init__(fig)
        Toolbar(self, None).pan()

    def create_figure(self):
        pass


class HistPlot(CustomCanvas):

    def create_figure(self):
        rdis, = self.data
        self.axes.set_title("Histogram for $r \\times (d_n - i \sqrt{n})$")
        self.axes.hist(rdis, min(int(len(rdis) ** .5), 30), edgecolor='k')


class PathPlot(CustomCanvas):

    def create_figure(self):
        xpos, ypos = self.data
        self.axes.set_title("Random walk")
        self.axes.plot(xpos, ypos, 'y-')
        self.axes.plot(xpos, ypos, 'b.', markersize=2)
        self.axes.plot(xpos[0], ypos[0], color='r', marker='$S$')
        self.axes.plot(xpos[-1], ypos[-1], color='r', marker='$E$')


class DistPlot(CustomCanvas):

    def create_figure(self):
        dist, expt = self.data
        self.axes.set_title("Distance comparison")
        rn, = self.axes.plot(dist, label='d')
        ex, = self.axes.plot(expt, label='√n')
        self.axes.legend(handles=[rn, ex], loc='upper left')
