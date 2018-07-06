#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, Qt
import pyqtgraph as pg
import sys
from signal_sdr import SignalSdr

data_folder = QtCore.QDir.homePath()

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
        self.clear_and_draw()

        self.signal_sdr.overlay_changed.connect(self.drawOverlay)
        self.signal_sdr.data_changed.connect(self.clear_and_draw)
        self.signal_sdr.code_changed.connect(self.drawCode)

    def clear_and_draw(self):
        self.clear()
        self.drawPoints()
        self.linearReg = pg.LinearRegionItem(movable=False)
        self.drawOverlay()
        self.scatterPlot = pg.ScatterPlotItem()
        self.addItem(self.linearReg)
        self.addItem(self.scatterPlot)

    def drawPoints(self):
        self.clear()
        self.plot(self.signal_sdr.points.index, self.signal_sdr.points['signal'].values)
        s_min = self.signal_sdr.points['signal'].min()
        s_max = self.signal_sdr.points['signal'].max()
        self.setLimits(yMin=s_min - 2,
                       yMax=s_max + 2, minYRange=s_max - s_min + 4)

    def drawOverlay(self):
        self.linearReg.setRegion([self.signal_sdr.start_tick,self.signal_sdr.end_tick])

    def drawCode(self):
        df = self.signal_sdr.points
        indexes = df[df['middle'] == True].index
        self.scatterPlot.setData(indexes, [self.signal_sdr.threshold] * len(indexes))
        '''
        self.textItems = []
        import ipdb; ipdb.set_trace()   
        for i in df[df['middle'] == True].index:
            self.textItems.append(pg.TextItem(df.loc[i]['val'],
                                              fill=(100,100,200,50), color=(0,0,0)))
            self.textItems[-1].setPos(i, self.signal_sdr.threshold)
            self.addItem(self.textItems[-1])
        '''

class SideViewWidget(QtGui.QWidget):
    DEFAULT_SAMPLE_FREQ = 96000
    DEFAULT_NB_OF_EDGES = 10
    DEFAULT_NB_OF_TICKS = 10
    DEFAULT_CLIP_BOUNDARIES = 10
    DEFAULT_MESSAG_MAX_SIZE = 1000000

    def __init__(self, signal_sdr):
        super().__init__()
        self.signal_sdr = signal_sdr
        self.signal_sdr.freq_changed.connect(self.freq_update)

        self.load_btn = QtGui.QPushButton("Load")
        self.load_btn.clicked.connect(self.on_load)

        self.clock_freq = QtGui.QLabel()
        self.clock_period = QtGui.QLabel()

        self.sample_freq = QtGui.QSpinBox()
        self.sample_freq.setRange(1, 10000000)
        self.sample_freq.setValue(self.signal_sdr.sample_freq)
        self.sample_freq.setPrefix("Signal sample freq : ")
        self.sample_freq.setSuffix(" Hz")
        self.sample_freq.valueChanged.connect(self.on_sample_freq)
        self.on_sample_freq()

        self.offset_start = QtGui.QSpinBox()
        self.offset_start.setRange(0, 1000)
        self.offset_start.setValue(0)
        self.offset_start.setPrefix("First edge offset : ")
        self.offset_start.valueChanged.connect(self.on_offset_start)
        self.on_offset_start()

        self.nb_of_edges = QtGui.QSpinBox()
        self.nb_of_edges.setRange(1, 1000)
        self.nb_of_edges.setValue(self.DEFAULT_NB_OF_EDGES)
        self.nb_of_edges.setPrefix("Number of edges : ")
        self.nb_of_edges.valueChanged.connect(self.on_nb_of_edges)
        self.on_nb_of_edges()

        self.nb_of_ticks_in_selection = QtGui.QSpinBox()
        self.nb_of_ticks_in_selection.setRange(1, 1000)
        self.nb_of_ticks_in_selection.setValue(self.DEFAULT_NB_OF_TICKS)
        self.nb_of_ticks_in_selection.setPrefix("Clock ticks in edges selection : ")
        self.nb_of_ticks_in_selection.valueChanged.connect(self.on_nb_of_ticks_in_selection)
        self.on_nb_of_ticks_in_selection()

        self.frequency_adjustement = QtGui.QDoubleSpinBox()
        self.frequency_adjustement.setRange(0, 2)
        self.frequency_adjustement.setValue(1)
        self.frequency_adjustement.setSingleStep(0.0001)
        self.frequency_adjustement.setDecimals(4)
        self.frequency_adjustement.setPrefix("coeff freq adjustement : ")
        self.frequency_adjustement.valueChanged.connect(self.on_freq_adjustement)
        self.on_freq_adjustement()

        self.clip_boundaries = QtGui.QSpinBox()
        self.clip_boundaries.setRange(1, 50)
        self.clip_boundaries.setValue(self.DEFAULT_CLIP_BOUNDARIES)
        self.clip_boundaries.setPrefix("distance from min/max to clip : ")
        self.clip_boundaries.valueChanged.connect(self.on_clip_boundaries)
        self.on_clip_boundaries()

        self.message_max_size = QtGui.QSpinBox()
        self.message_max_size.setRange(100000, 10000000)
        self.message_max_size.setValue(self.DEFAULT_MESSAG_MAX_SIZE)
        self.message_max_size.setPrefix("max message number of points : ")
        self.message_max_size.valueChanged.connect(self.on_message_max_size)
        self.on_message_max_size()

        self.find_code_button = QtGui.QPushButton("GO !")
        self.find_code_button.clicked.connect(self.on_find_code)

        self.code_result = QtGui.QPlainTextEdit()
        self.code_result.resize(390,200)
        self.code_result.setMaximumHeight(200)
        self.code_result.setReadOnly(True)
        self.signal_sdr.code_changed.connect(self.on_code_found)

        layout = QtGui.QGridLayout()
        layout.addWidget(self.load_btn, 0, 0)
        layout.addWidget(self.sample_freq, 1, 0)
        layout.addWidget(self.offset_start, 2, 0)
        layout.addWidget(self.nb_of_edges, 3, 0)
        layout.addWidget(self.nb_of_ticks_in_selection, 4, 0)
        layout.addWidget(self.frequency_adjustement, 5, 0)
        layout.addWidget(self.clock_freq, 6, 0)
        layout.addWidget(self.clock_period, 7, 0)
        layout.addWidget(self.clip_boundaries, 8, 0)
        layout.addWidget(self.message_max_size, 9, 0)
        layout.addWidget(self.find_code_button, 10, 0)
        layout.addWidget(self.code_result, 11, 0)

        self.setLayout(layout)

    def freq_update(self):
        self.clock_freq.setText("clock freq : " +
                                str(round(self.signal_sdr.clock_freq, 5)) + " Hz")
        self.clock_period.setText("clock period : " +
                                  str(round(1 / (self.signal_sdr.clock_freq) * 1000, 5)) + " ms")

    def on_load(self):
        filename, _ = QtGui.QFileDialog.getOpenFileName(self.load_btn.parent(),
                          "Open File")#, data_folder, "All Files (*)")
        print(filename)
        self.signal_sdr.open_new_file(filename)

        self.sample_freq.setValue(self.signal_sdr.sample_freq)
        self.nb_of_edges.setValue(self.DEFAULT_NB_OF_EDGES)
        self.nb_of_ticks_in_selection.setValue(self.DEFAULT_NB_OF_TICKS)
        self.offset_start.setValue(0)

    def on_offset_start(self):
        self.signal_sdr.offset_start_change(self.offset_start.value())

    def on_nb_of_edges(self):
        self.signal_sdr.nb_of_edges_change(self.nb_of_edges.value())

    def on_nb_of_ticks_in_selection(self):
        self.signal_sdr.nb_of_ticks_in_selection_change(self.nb_of_ticks_in_selection.value())

    def on_sample_freq(self):
        self.signal_sdr.sample_freq_change(self.sample_freq.value())

    def on_freq_adjustement(self):
        self.signal_sdr.freq_adjustement_change(self.frequency_adjustement.value())

    def on_clip_boundaries(self):
        self.signal_sdr.clip_boundaries_change(self.clip_boundaries.value())

    def on_message_max_size(self):
        self.signal_sdr.message_max_size_change(self.message_max_size.value())

    def on_find_code(self):
        self.signal_sdr.find_code_push()

    def on_code_found(self):
        df = self.signal_sdr.points
        text_code = ''
        for v in df['val'][df['middle'] == True]:
            text_code += v
        self.code_result.setPlainText(text_code)
        with open('arduino_header.txt', 'w') as f:
            f.write("bool message[] =")
            mess = '{'
            for c in text_code: mess += c + ','
            f.write(mess + '0};\n')
            f.write('int message_size = ' + str(len(text_code) + 1) + ';\n')
            f.write('int freq_ms = ' + str(int(round(1 / self.signal_sdr.clock_freq * 1000000))) +\
                    ';')


if __name__ == '__main__':
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    pg.setConfigOption('antialias', True)
    app = QtGui.QApplication([])

    signal_sdr = SignalSdr('../garage_1_8M.wav')
    #signal_sdr = SignalSdr('../small.wav')

    data_plot_widget = DataPlotWidget(signal_sdr)
    side_view_widget = SideViewWidget(signal_sdr)

    main_widget = MainWidget(data_plot_widget, side_view_widget)
    main_widget.show()


    sys.exit(app.exec_())
