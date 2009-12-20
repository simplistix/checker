# Copyright (c) 2009 Simplistix Ltd
#
# See license.txt for more details.
from __future__ import with_statement

import os

from checker import command
from os.path import join

def check(config_folder,daemon):
    inits = join(config_folder,'init')
    if not os.path.exists(inits):
        os.mkdir(inits)
    with open(join(inits,daemon),'wb') as f:
        for row in command.execute(
            'update-rc.d -n -f %s remove'%daemon
            ).split('\n'):
            row = row.strip()
            if row.startswith('Removing'):
                continue
            print >>f,row
            
    return ''
    
