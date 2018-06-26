#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, Qt
import pyqtgraph as pg
import sys
import utils


class MainWidget(QtGui.QSplitter):
    def __init__(self, data_plot_widget, side_view_widget):
        super().__init__(QtCore.Qt.Horizontal)
        self.data_plot_widget = data_plot_widget
        self.side_view_widget = side_view_widget

        self.resize(1500, 800)

        self.addWidget(self.side_view_widget)
        self.addWidget(self.data_plot_widget)

class DataPlotWidget(pg.PlotWidget):
    def __init__(self):
        super().__init__()
        self.drawPoints()

    def drawPoints(self):
        points = [[],[]]

        data = utils.round_data(utils.get_data('../output.wav'))
        for i, val in enumerate(data):
            points[0].append(i)
            points[1].append(val)

        self.plot(points[0], points[1])
        self.setLimits(yMin=125, yMax=158, minYRange=33)


class SideViewWidget(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        #self.setMaximumSize(200, 

if __name__ == '__main__':
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    pg.setConfigOption('antialias', True)
    app = QtGui.QApplication([])

    data_plot_widget = DataPlotWidget()
    side_view_widget = SideViewWidget()

    main_widget = MainWidget(data_plot_widget, side_view_widget)
    main_widget.show()


    sys.exit(app.exec_())
