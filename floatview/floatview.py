#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Project Jupyter.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""

from ipywidgets import Output
from traitlets import Unicode,Bool
from ._version import EXTENSION_SPEC_VERSION

module_name = "@jupyter-widgets/jupyterlab-floatview"


class Floatview(Output):
    _model_name = Unicode('FloatviewModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(EXTENSION_SPEC_VERSION).tag(sync=True)
    _view_name = Unicode('FloatviewView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(EXTENSION_SPEC_VERSION).tag(sync=True)
    title = Unicode('Floatview').tag(sync=True)
    mode = Unicode('tab-after').tag(sync=True)
    uid = Unicode('').tag(sync=True)
    active = Bool(False).tag(sync=True)

    def __init__(self, *args, **kwargs):
        super(Floatview, self).__init__(*args, **kwargs)    

