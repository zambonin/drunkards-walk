#!/usr/bin/env python

from math import cos, sin
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as Toolbar
from matplotlib.pyplot import subplots
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QSize
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget,             \
    QGroupBox, QHBoxLayout, QSpinBox, QVBoxLayout, QProgressBar,            \
    QPushButton, QDesktopWidget, QLabel
from random import random
from sys import argv, exit


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
        self.axes.hist(rdis, min(int(len(rdis) ** .5), 30))


class PathPlot(CustomCanvas):

    def create_figure(self):
        xpos, ypos = self.data
        self.axes.set_title("Random walk")
        self.axes.plot(xpos, ypos)
        self.axes.plot(xpos, ypos, 'b.', markersize=2)
        self.axes.plot(xpos[0], ypos[0], marker='$S$')
        self.axes.plot(xpos[-1], ypos[-1], marker='$E$')


class DistPlot(CustomCanvas):

    def create_figure(self):
        dist, expt = self.data
        self.axes.set_title("Distance comparison")
        rn, = self.axes.plot(dist, label='d')
        ex, = self.axes.plot(expt, label='√n')
        self.axes.legend(handles=[rn, ex], loc='upper left')


class MonteCarloSim(QThread):

    prr_signal = pyqtSignal(int)
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
                angle = int(random() * 360)
                xpos[i] = xpos[i - 1] + (i + 1) * cos(angle)
                ypos[i] = ypos[i - 1] + (i + 1) * sin(angle)
                dist[i] = (xpos[i] ** 2 + ypos[i] ** 2) ** .5
                expt[i] = self.iterations * (i ** .5)
            rdis[r] = dist[-1] - expt[-1]
            self.prr_signal.emit(r + 1)

        self.plt_signal.emit(xpos, ypos, dist, expt, rdis)


class ApplicationWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Drunkard's Walk Simulator")
        self.setFixedSize(QSize(225, 275))

        self.it_box = QSpinBox()
        self.it_box.setRange(1, (1 << 31) - 1)
        self.it_box.setSingleStep(100)
        self.it_box.setValue(2000)

        self.rp_box = QSpinBox()
        self.rp_box.setRange(1, (1 << 31) - 1)
        self.rp_box.setSingleStep(10)
        self.rp_box.setValue(1)

        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.process_data)

        self.prr_bar = QProgressBar()
        self.prr_bar.setValue(0)

        it_group = QGroupBox("Number of iterations (i)")
        it_layout = QHBoxLayout(it_group)
        it_layout.addWidget(self.it_box)

        rp_group = QGroupBox("Number of replications (r)")
        rp_layout = QHBoxLayout(rp_group)
        rp_layout.addWidget(self.rp_box)

        pr_group = QGroupBox("Progress bar (r)")
        pr_layout = QHBoxLayout(pr_group)
        pr_layout.addWidget(self.prr_bar)
        pr_layout.addWidget(self.start_button)

        parameters = QGroupBox("Simulation info and parameters")
        param_layout = QVBoxLayout(parameters)
        param_layout.addWidget(it_group)
        param_layout.addWidget(rp_group)
        param_layout.addWidget(pr_group)

        self.main_widget = QWidget(self)
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.addWidget(parameters)
        self.setCentralWidget(self.main_widget)

    def process_data(self):

        self.rp_box.setEnabled(False)
        self.it_box.setEnabled(False)
        self.start_button.setText("Abort/quit")
        self.start_button.disconnect()
        self.start_button.clicked.connect(self.close)

        r, i = self.rp_box.value(), self.it_box.value()
        self.prr_bar.setMaximum(r)

        self.thread = MonteCarloSim(r, i)
        self.thread.prr_signal.connect(self.prr_bar.setValue)
        self.thread.plt_signal.connect(self.add_graphs)
        self.thread.start()

    def add_graphs(self, xpos, ypos, dist, expt, rdis):

        self.start_button.setText("Quit")
        if len(rdis) > 1:
            self.main_layout.addWidget(HistPlot(rdis))
            self.setFixedSize(QSize(640, 432))
        else:
            self.main_layout.addWidget(PathPlot(xpos, ypos))
            self.main_layout.addWidget(DistPlot(dist, expt))
            self.setFixedSize(QSize(1152, 432))
            dist_label = QLabel("Difference between distances: {:.2f} units"
                                .format(rdis[-1]))
            dist_label.setAlignment(Qt.AlignRight)
            self.statusBar().addWidget(dist_label, 1)

        resolution = QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))
        self.statusBar().showMessage(
                'Left click and drag to pan, right click and drag to zoom')


if __name__ == '__main__':
    app = QApplication(argv)
    aw = ApplicationWindow()
    aw.show()
    exit(app.exec_())
