#!/usr/bin/env python

from .custom_canvas import DistPlot, HistPlot, PathPlot
from .monte_carlo import MonteCarloSim
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QDesktopWidget, QGroupBox, QHBoxLayout, QLabel, \
    QMainWindow, QProgressBar, QPushButton, QSpinBox, QVBoxLayout, QWidget


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

        self.start_button = QPushButton("Start", self, default=True)
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

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return:
            self.process_data()

    def process_data(self):
        self.rp_box.setEnabled(False)
        self.it_box.setEnabled(False)
        self.start_button.setText("Abort/quit")
        self.start_button.disconnect()
        self.start_button.clicked.connect(self.close)

        r, i = self.rp_box.value(), self.it_box.value()
        self.thread = MonteCarloSim(r, i)

        if r != 1:
            self.prr_bar.setMaximum(r)
            self.thread.prr_signal.connect(self.prr_bar.setValue)
        else:
            self.prr_bar.setMaximum(i)
            self.thread.pri_signal.connect(self.prr_bar.setValue)

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
