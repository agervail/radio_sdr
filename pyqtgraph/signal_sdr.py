#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, Qt
from scipy.io import wavfile
import pandas as pd
import numpy as np

class SignalSdr(QtCore.QObject):
    data_changed = QtCore.pyqtSignal()
    overlay_changed = QtCore.pyqtSignal()
    freq_changed = QtCore.pyqtSignal()
    code_changed = QtCore.pyqtSignal()

    def __init__(self, filename = None):
        super().__init__()
        self.open_new_file(filename)

    def open_new_file(self, filename):
        self.filename = filename
        self.start = 0
        self.end = 0
        self.points = None
        self.original_points = None
        self.threshold = 0
        self.start_tick = 0
        self.end_tick = 0
        self.nb_of_edges = 10
        self.clock_freq = 0
        self.nb_of_ticks_in_selection = 1
        self.points_in_one_tick = 0
        self.sample_freq = 96000
        self.freq_adjustement = 1
        self.index_middle_tick = None
        self._init_data(filename)
        self._update_clock_freq()
        self.data_changed.emit()

    def offset_start_change(self, offset_start):
        self._find_start_end_tick(offset_start, offset_start + self.nb_of_edges)
        self._update_overlay()

    def nb_of_edges_change(self, nb_of_edges):
        self.nb_of_edges = nb_of_edges
        self.end_tick = self.points.index[(self.points['rising'] |
                                           self.points['falling'])][self.nb_of_edges]
        self._update_overlay()
        self._update_clock_freq()

    def nb_of_ticks_in_selection_change(self, nb_of_ticks_in_selection):
        self.nb_of_ticks_in_selection = nb_of_ticks_in_selection
        self._update_clock_freq()

    def sample_freq_change(self, sample_freq):
        self.sample_freq = sample_freq
        self._update_clock_freq()

    def freq_adjustement_change(self, freq_adjustement):
        self.freq_adjustement = freq_adjustement
        self._update_clock_freq()

    def find_code_push(self):
        self.points = self.original_points
        half_period = self.points_in_one_tick / 2
        start_index = int(self.start + half_period)
        index_middle_tick = [int(i) for i in np.arange(start_index, self.end,
                             self.points_in_one_tick * self.freq_adjustement)]

        df = pd.DataFrame(True, index=index_middle_tick, columns=['middle'])
        df = pd.concat([self.points, df], axis=1)
        df['signal'] = df['signal'].interpolate()

        df['val'] = df[df['middle'] == True].apply(lambda row: '1' if row['signal'] > self.threshold
                                                                else '0', axis=1)
        self.points = df

        #import matplotlib.pyplot as plt
        #df[df['middle'] == True]['signal'].plot()
        #df['signal'].plot()
        #import ipdb; ipdb.set_trace()
        #plt.show()

        self.code_changed.emit()

    def clip_boundaries_change(self, clip_boundaries):
        self._init_data(self.filename, clip_boundaries=clip_boundaries)
        self.data_changed.emit()

    def message_max_size_change(self, message_max_size):
        self._init_data(self.filename,message_max_size=message_max_size)
        self.data_changed.emit()

    def _update_overlay(self):
        self.overlay_changed.emit()

    def _update_clock_freq(self):
        self.points_in_one_tick = (self.end_tick - self.start_tick) / self.nb_of_ticks_in_selection
        self.clock_freq = self.sample_freq / (self.points_in_one_tick * self.freq_adjustement)
        self.freq_changed.emit()

    def _find_start_end_tick(self, begin, end):
        df = self.points
        self.start_tick = df.index[df['rising'] | df['falling']][begin]
        self.end_tick = df.index[df['rising'] | df['falling']][end]


    def _init_data(self, filename, clip_boundaries=10, message_max_size=1000000):
        self.sample_freq, k = wavfile.read(filename)
        df = pd.DataFrame(k, columns=['signal'])
        s_min = df['signal'].min()
        s_max = df['signal'].max()
        df = df.clip(s_min + clip_boundaries, s_max - clip_boundaries)
        df = df.loc[(df['signal'].shift() != df['signal'])
                    | (df['signal'].shift(-1) != df['signal']), ['signal']]

        self.threshold = s_min + (s_max - s_min) / 2

        df['rising'] = (df['signal'] > self.threshold) & (df['signal'].shift() <= self.threshold)
        df['falling'] = (df['signal'] < self.threshold) & (df['signal'].shift() >= self.threshold)

        #message_max_size = 1000000
        self.start = (min(df['rising'].idxmax(), df['falling'].idxmax()))
        self.end = (max(df.loc[self.start+message_max_size:self.start:-1]['rising'].idxmax(),
                        df.loc[self.start+message_max_size:self.start:-1]['falling'].idxmax()))

        self.points = df.loc[self.start:self.end]
        self._find_start_end_tick(0, self.nb_of_edges)
        self.original_points = self.points.copy()
