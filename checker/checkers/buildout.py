# Copyright (c) 2009-2010 Simplistix Ltd
#
# See license.txt for more details.

import os

import execute

def check(config_folder,path):
    return execute.simple(
        'bin'+os.sep+'buildout -o -q',
        cwd=path
        )
