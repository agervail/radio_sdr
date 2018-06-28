#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, Qt
from scipy.io import wavfile
import pandas as pd

class SignalSdr(QtCore.QObject):
    data_changed = QtCore.pyqtSignal()
    overlay_changed = QtCore.pyqtSignal()
    freq_changed = QtCore.pyqtSignal()

    def __init__(self, filename = None):
        super().__init__()
        self.start = 0
        self.end = 0
        self.points = None
        self.start_tick = 0
        self.end_tick = 0
        self.clock_freq = 0
        self.nb_of_ticks_in_selection = 1
        self.sample_freq = 96000
        self._init_data(filename)
        self.freq_changed.emit()

    def nb_of_edges_change(self, nb_of_edges):
        self.end_tick = self.points.index[(self.points['rising'] |
                                           self.points['falling'])][nb_of_edges]
        self._update_overlay()
        self._update_clock_freq()
        self.freq_changed.emit()

    def nb_of_ticks_in_selection_change(self, nb_of_ticks_in_selection):
        self.nb_of_ticks_in_selection = nb_of_ticks_in_selection
        self._update_clock_freq()
        self.freq_changed.emit()

    def sample_freq_change(self, sample_freq):
        self.sample_freq = sample_freq
        self._update_clock_freq()
        self.freq_changed.emit()

    def _update_overlay(self):
        self.overlay_changed.emit()

    def _update_clock_freq(self):
        one_tick = (self.end_tick - self.start_tick) / self.nb_of_ticks_in_selection
        self.clock_freq = one_tick * (1 / (self.sample_freq * 1000))

    def _init_data(self, filename):
        k = wavfile.read(filename)[1]
        df = pd.DataFrame(k, columns=['signal'])
        s_min = df['signal'].min()
        s_max = df['signal'].max()
        df = df.clip(s_min + 10, s_max - 10)
        df = df.loc[(df['signal'].shift() != df['signal'])
                    | (df['signal'].shift(-1) != df['signal']), ['signal']]

        threshold = s_min + (s_max - s_min) / 2

        df['rising'] = (df['signal'] < threshold) & (df['signal'].shift() >= threshold)
        df['falling'] = (df['signal'] > threshold) & (df['signal'].shift() <= threshold)

        message_max_size = 200000
        self.start = (min(df['rising'].idxmax(), df['falling'].idxmax()))
        self.end = (min(df.loc[self.start+message_max_size:self.start:-1]['rising'].idxmax(),
                        df.loc[self.start+message_max_size:self.start:-1]['falling'].idxmax()))

        self.start_tick = df.index[df['rising'] | df['falling']][0]
        self.end_tick = df.index[df['rising'] | df['falling']][1]
        self.points = df.loc[self.start:self.end]
