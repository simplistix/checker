# Copyright (c) 2010 Simplistix Ltd
#
# See license.txt for more details.

import os

import execute
from os.path import join

def check(config_folder,param):
    filename,command = param.split(':',1)
    f = open(join(config_folder,filename),'wb')
    f.write(execute.simple(command))
    f.close()
    return ''
