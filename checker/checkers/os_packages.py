# Copyright (c) 2010-2014 Simplistix Ltd
#
# See license.txt for more details.
import os
import execute

def check(config_folder,junk):
    with open(os.path.join(config_folder, 'os_packages'), 'wb') as out:
        for possible in (
            'dpkg -l',
            'yum list',
            'up2date --showall',
            ):
            if execute.returncode('which '+possible.split()[0])!=0:
                continue
            out.write(execute.simple(possible))
            return ''
    return 'Could not find package manager!'
    
