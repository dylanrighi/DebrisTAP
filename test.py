#!/usr/bin/env python

import os, sys, string, math
from datetime import datetime, timedelta
import importlib

import gnome
from gnome.spill import point_line_release_spill
from gnome.outputters import Renderer, NetCDFOutput

from TAP_Setup import setup


start_positions = [(211.317, 70.492), (196.306, 71.2612)]
start_dt = [datetime(1985, 4, 24, 16, 0),
            datetime(1985, 4, 13, 0, 0),
            datetime(1985, 6, 19, 14, 0)]

for pos_idx, start_position in enumerate(start_positions):
    for time_idx, start_time in enumerate(start_dt):
        print pos_idx, time_idx
