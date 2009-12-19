# Copyright (c) 2009 Simplistix Ltd
#
# See license.txt for more details.

import os

from checker import command

def check(config_folder,path):
    return command.execute(
        'bin'+os.sep+'buildout -o -q',
        cwd=path
        )
