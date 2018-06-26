#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, Qt
from scipy.io import wavfile

class SignalSdr(QtCore.QObject):
    data_changed = QtCore.pyqtSignal()
    overlay_changed = QtCore.pyqtSignal()

    def __init__(self, filename = None):
        super().__init__()
        self.start = 0
        self.end = 0
        self.points = [[],[]]
        self.rising = []
        self.falling = []
        self.risfall = []
        self.start_tick = 0
        self.end_tick = 0
        self._init_data(filename)

    def nb_of_clock_change(self, nb_of_clock):
        self.end_tick = self.risfall[nb_of_clock]
        self._update_overlay()
        print(nb_of_clock)


    def _update_overlay(self):
        self.overlay_changed.emit()

    def _init_data(self, filename):
        k = wavfile.read(filename)[1]
        message_max_size = 200000
        threshold = 150

        self.start = 0
        for i, val in enumerate(k[1:]):
            if k[i] < threshold and val >= threshold:
                if self.start == 0:
                    self.start = i
                self.rising.append(i)
                self.risfall.append(i)
            if k[i] > threshold and val <= threshold:
                self.end = i
                self.falling.append(i)
                self.risfall.append(i)

        raw = k[self.start - 20:self.start - 20 + message_max_size]
        rounded = self._round_data(raw)

        for i, val in enumerate(rounded):
            self.points[0].append(i + self.start - 20)
            self.points[1].append(val)

        self.start_tick = self.risfall[0]
        self.end_tick = self.risfall[1]

    def _round_data(self, data):
        minV = 128
        maxV = 153
        middle = minV + (maxV - minV) / 2
        return [minV if x < middle else maxV for x in data]
