# Copyright (c) 2010 Simplistix Ltd
#
# See license.txt for more details.

import os

import execute
from os.path import join

def check(config_folder,junk):
    for possible in (
        'dpkg -l',
        'yum list',
        'up2date --showall',
        ):
        if execute.returncode('which '+possible.split()[0])!=0:
            continue
        f = open(os.path.join(config_folder,'os_packages'),'wb')
        f.write(execute.simple(possible))
        f.close()
        break
    return ''
    
