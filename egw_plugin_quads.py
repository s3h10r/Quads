#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
egw-filter Quads
"""
import logging
import random
import string
import sys
from PIL import Image
from einguteswerkzeug.plugins import EGWPluginFilter
from .main import main as quads_main

fmeta = {
    "name" : "quads",
    "version" : "0.1.2",
    "description" : "based on https://github.com/fogleman/Quads",
    "author" : "Michael Fogleman"
}

class Quads(EGWPluginFilter):
    def __init__(self, **kwargs):
        super().__init__(**fmeta)
        # defining mandatory kwargs (addionals to the mandatory of the base-class)
        add_kwargs = {  'mode' : random.randint(1,3),
                        'iterations' : 1024,
                        'leaf_size'  : 4,
                        'padding'    : 1,
                        'fill_color' : (255,255,255),
                        'error_rate' : 0.5,
                        'area_power' : 0.25,
                        'output_scale' : 1,
                        }
        self._define_mandatory_kwargs(self, **add_kwargs)
        self.kwargs = kwargs

    def run(self):
        return quads_main(**self._kwargs)


filter = Quads()
assert isinstance(filter,EGWPluginFilter)
