#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, Qt
import pyqtgraph as pg
import sys
from signal_sdr import SignalSdr

class MainWidget(QtGui.QSplitter):
    def __init__(self, data_plot_widget, side_view_widget):
        super().__init__(QtCore.Qt.Horizontal)
        self.data_plot_widget = data_plot_widget
        self.side_view_widget = side_view_widget

        self.resize(1500, 800)

        self.addWidget(self.side_view_widget)
        self.addWidget(self.data_plot_widget)

        self.setSizes([400,1100])

class DataPlotWidget(pg.PlotWidget):
    def __init__(self, signal_sdr):
        super().__init__()
        self.signal_sdr = signal_sdr
        self.drawPoints()
        self.linearReg = pg.LinearRegionItem(movable=False)
        self.drawOverlay()
        self.addItem(self.linearReg)

        self.signal_sdr.overlay_changed.connect(self.drawOverlay)

    def drawPoints(self):
        self.plot(self.signal_sdr.points.index, self.signal_sdr.points['signal'].values)
        self.setLimits(yMin=125, yMax=158, minYRange=33)

    def drawOverlay(self):
        self.linearReg.setRegion([self.signal_sdr.start_tick,self.signal_sdr.end_tick])
        print(self.signal_sdr.start_tick, self.signal_sdr.end_tick)


class SideViewWidget(QtGui.QWidget):
    def __init__(self, signal_sdr):
        super().__init__()
        self.signal_sdr = signal_sdr
        self.signal_sdr.freq_changed.connect(self.freq_update)

        self.sample_freq = QtGui.QSpinBox()
        self.sample_freq.setRange(1, 1000000)
        self.sample_freq.setValue(96000)
        self.sample_freq.setPrefix("Signal sample freq : ")
        self.sample_freq.setSuffix("KHz")
        self.sample_freq.valueChanged.connect(self.on_sample_freq)

        self.nb_of_edges = QtGui.QSpinBox()
        self.nb_of_edges.setRange(1, 1000)
        self.nb_of_edges.setValue(1)
        self.nb_of_edges.setPrefix("Number of edges : ")
        self.nb_of_edges.valueChanged.connect(self.on_nb_of_edges)

        self.nb_of_ticks_in_selection = QtGui.QSpinBox()
        self.nb_of_ticks_in_selection.setRange(1, 1000)
        self.nb_of_ticks_in_selection.setValue(1)
        self.nb_of_ticks_in_selection.setPrefix("Clock ticks in edges selection : ")
        self.nb_of_ticks_in_selection.valueChanged.connect(self.on_nb_of_ticks_in_selection)

        self.clock_freq = QtGui.QLabel("clock freq : 0")

        layout = QtGui.QGridLayout()
        layout.addWidget(self.sample_freq, 0, 0)
        layout.addWidget(self.nb_of_edges, 1, 0)
        layout.addWidget(self.nb_of_ticks_in_selection, 2, 0)
        layout.addWidget(self.clock_freq, 3, 0)

        self.setLayout(layout)

    def freq_update(self):
        self.clock_freq.setText("clock freq : " + str(self.signal_sdr.clock_freq))

    def on_nb_of_edges(self):
        self.signal_sdr.nb_of_edges_change(self.nb_of_edges.value())

    def on_nb_of_ticks_in_selection(self):
        self.signal_sdr.nb_of_ticks_in_selection_change(self.nb_of_ticks_in_selection.value())

    def on_sample_freq(self):
        self.signal_sdr.sample_freq_change(self.sample_freq.value())

if __name__ == '__main__':
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    pg.setConfigOption('antialias', True)
    app = QtGui.QApplication([])

    signal_sdr = SignalSdr('../output.wav')
    #signal_sdr = SignalSdr('../small.wav')

    data_plot_widget = DataPlotWidget(signal_sdr)
    side_view_widget = SideViewWidget(signal_sdr)

    main_widget = MainWidget(data_plot_widget, side_view_widget)
    main_widget.show()


    sys.exit(app.exec_())
