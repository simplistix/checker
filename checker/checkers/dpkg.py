# Copyright (c) 2009-2010 Simplistix Ltd
#
# See license.txt for more details.

import os

import execute
from os.path import join

def check(config_folder,junk):
    f = open(os.path.join(config_folder,'dpkg'),'wb')
    f.write(execute.simple('dpkg -l'))
    f.close()
    return ''
    
