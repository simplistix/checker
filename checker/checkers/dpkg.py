# Copyright (c) 2009 Simplistix Ltd
#
# See license.txt for more details.

import os

from checker import command
from os.path import join

def check(config_folder,junk):
    f = open(os.path.join(config_folder,'dpkg'),'wb')
    f.write(command.execute('dpkg -l'))
    f.close()
    return ''
    
