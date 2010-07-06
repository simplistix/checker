# Copyright (c) 2009-2010 Simplistix Ltd
#
# See license.txt for more details.

import os

import execute
from os.path import join

def check(config_folder,user):
    crontabs = join(config_folder,'crontabs')
    if not os.path.exists(crontabs):
        os.mkdir(crontabs)
    f = open(join(crontabs,user),'wb')
    f.write(execute.simple('crontab -l -u '+user))
    f.close()
    return ''
    
