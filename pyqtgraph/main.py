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
        self.plot(self.signal_sdr.points[0], self.signal_sdr.points[1])
        self.setLimits(yMin=125, yMax=158, minYRange=33)

    def drawOverlay(self):
        self.linearReg.setRegion([self.signal_sdr.start_tick,self.signal_sdr.end_tick])
        print(self.signal_sdr.start_tick, self.signal_sdr.end_tick)


class SideViewWidget(QtGui.QWidget):
    def __init__(self, signal_sdr):
        super().__init__()
        self.signal_sdr = signal_sdr

        self.nb_of_clock = QtGui.QSpinBox()
        self.nb_of_clock.setRange(1, 1000)
        self.nb_of_clock.setValue(1)
        self.nb_of_clock.setPrefix("Number of clock ticks : ")
        self.nb_of_clock.valueChanged.connect(self.on_nb_of_clock)


        layout = QtGui.QGridLayout()
        layout.addWidget(self.nb_of_clock, 0, 0)

        self.setLayout(layout)

    def on_nb_of_clock(self):
        self.signal_sdr.nb_of_clock_change(self.nb_of_clock.value())

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
