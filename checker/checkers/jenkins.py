# Copyright (c) 2012 Simplistix Ltd
#
# See license.txt for more details.

from glob import glob
from os import sep, makedirs
from os.path import join, dirname, exists
from shutil import copyfile

def _paths(jenkins_home):
    for pattern in ['*.xml'], ['jobs', '*', 'config.xml']:
        for path in glob(join(jenkins_home, *pattern)):
            yield path
            
def check(config_folder, jenkins_home):
    for src_path in _paths(jenkins_home):
        target_path = join(config_folder, *src_path.split(sep)[1:])
        target_dir = dirname(target_path)
        if not exists(target_dir):
            makedirs(target_dir)
        copyfile(src_path, target_path)
    
    return ''
    
