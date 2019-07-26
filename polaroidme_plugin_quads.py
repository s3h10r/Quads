#!/usr/bin/env python
#coding=utf-8
# === polaroidme plugin-interface ===
# --- all polaroidme-plugins (generators, filters) must implement this
import logging
import string

name = "quads"
description = "https://github.com/fogleman/Quads"
kwargs = {  'mode' : 2,
            'iterations' : 1024,
            'leaf_size'  : 4,
            'padding'    : 1,
            'fill_color' : (0,0,0),
            'error_rate' : 0.5,
            'area_power' : 0.25,
            'output_scale' : 1,
         }
args = None
author = "Michael Fogleman"
version = "0.1.0"

def run(**kwargs):
    """
    this is the interface/wrapper around the functionality of the plugin.
    """
    #call the plugin-specific function(s) here
    if not kwargs :
        #use default values if no args given
        return _somework()
    else:
        return _somework(**kwargs)

# --- END all polaroidme-plugins (generators, filters) must implement this

def get_plugin_doc(format='text'):
    """
    """
    if format not in ('txt', 'text', 'plaintext'):
        raise Exception("Sorry. format %s not available. Valid options are ['text']" % format)
    tpl_doc = string.Template("""
    filters.$name - $description
    kwargs  : $kwargs
    args    : $args
    author  : $author
    version : __version__
    """)
    return tpl_doc.substitute({
        'name' : name,
        'description' : description,
        'kwargs' : kwargs,
        'args'    : args,
        'author'  : author,
        'version' : __version__,
        })

if __name__ == '__main__':
    print(get_plugin_doc())

# === END polaroidme plugin-interface

# --- .. here comes the plugin-specific part to get some work done...
def _somework(arg1=None, arg2 = None):
    return ("Hello from Plugin dummy1. arg1=%s, arg2=%s " % (arg1,arg2))
