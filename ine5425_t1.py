#!/usr/bin/env python

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FCanvas
from matplotlib.pyplot import subplots
from math import cos, sin
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget,             \
    QGridLayout, QGroupBox, QHBoxLayout, QSpinBox, QVBoxLayout,             \
    QProgressBar, QPushButton, QDesktopWidget
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from random import random
from sys import argv, exit


class CustomCanvas(FCanvas):
    def __init__(self, data, parent):
        fig, self.axes = subplots()
        self.axes.ticklabel_format(style='sci', scilimits=(0, 0))
        self.data = data

        self.compute_initial_figure()

        FCanvas.__init__(self, fig)
        self.setParent(parent)

        FCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class HistPlot(CustomCanvas):

    def compute_initial_figure(self):
        self.axes.set_title("Histograma para $r \\times (d_n - i \sqrt{n})$")
        self.axes.hist(self.data, min(int(len(self.data) ** .5), 30))


class PathPlot(CustomCanvas):

    def compute_initial_figure(self):
        xpos, ypos = self.data
        self.axes.set_title("Caminho percorrido")
        self.axes.plot(xpos, ypos)
        self.axes.plot(xpos, ypos, 'b.', markersize=2)
        self.axes.plot(xpos[0], ypos[0], 'rD')
        self.axes.plot(xpos[-1], ypos[-1], 'gD')


class DistPlot(CustomCanvas):

    def compute_initial_figure(self):
        dist, expt = self.data
        self.axes.set_title("Distância percorrida")
        rn, = self.axes.plot(range(len(dist)), dist, label='d')
        ex, = self.axes.plot(range(len(expt)), expt, label='√n')
        self.axes.legend(handles=[rn, ex], loc='upper left')


class NumberCrunching(QThread):

    prr_signal = pyqtSignal(int)
    pri_signal = pyqtSignal(int)
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
                # self.pri_signal.emit(i + 1)
            rdis[r] = dist[-1] - expt[-1]
            self.prr_signal.emit(r + 1)

        self.plt_signal.emit(xpos, ypos, dist, expt, rdis)


class ApplicationWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Drunkard's Walk Simulator")

        self.main_widget = QWidget(self)
        self.main_layout = QGridLayout(self.main_widget)

        it_group, self.it_box = self.create_spingroup(
            "Number of iterations (i)", 10, 500)
        rp_group, self.rp_box = self.create_spingroup(
            "Number of replications (r)", 5, 100)

        self.parameters = QGroupBox("Simulation info and parameters")
        param_layout = QVBoxLayout()

        pr_group = QGroupBox("Progress bar (r)")
        pr_layout = QHBoxLayout()
        self.start_button = QPushButton("Iniciar", self)
        self.start_button.clicked.connect(self.process_data)
        self.prr_bar = QProgressBar()
        self.prr_bar.setValue(0)
        pr_layout.addWidget(self.prr_bar)
        pr_layout.addWidget(self.start_button)
        pr_group.setLayout(pr_layout)

        param_layout.addWidget(it_group)
        param_layout.addWidget(rp_group)
        param_layout.addWidget(pr_group)
        self.parameters.setLayout(param_layout)

        self.main_layout.addWidget(self.parameters, 0, 0)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def create_spingroup(self, name, step, init):
        group, layout, box = QGroupBox(name), QHBoxLayout(), QSpinBox(self)
        box.setRange(0, (1 << 31) - 1)
        box.setSingleStep(step)
        box.setValue(init)
        layout.addWidget(box)
        group.setLayout(layout)
        return group, box

    def add_graphs(self, xpos, ypos, dist, expt, rdis):

        self.start_button.setText("Sair")
        self.resize(1024, 768)
        resolution = QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))
        self.main_layout.addWidget(HistPlot(rdis, self.main_widget), 0, 1)
        self.main_layout.addWidget(
            PathPlot((xpos, ypos), self.main_widget), 1, 0)
        self.main_layout.addWidget(
            DistPlot((dist, expt), self.main_widget), 1, 1)

    def process_data(self):

        self.start_button.setText("Parar e sair")
        self.start_button.disconnect()
        self.start_button.clicked.connect(self.close)

        r, i = self.rp_box.value(), self.it_box.value()

        self.prr_bar.setMaximum(r)
        # self.pri_bar.setMaximum(i)
        self.thread = NumberCrunching(r, i)
        self.thread.start()
        self.thread.prr_signal.connect(self.prr_bar.setValue)
        # self.thread.pri_signal.connect(self.pri_bar.setValue)
        self.thread.plt_signal.connect(self.add_graphs)


qApp = QApplication(argv)

aw = ApplicationWindow()
aw.show()
exit(qApp.exec_())
