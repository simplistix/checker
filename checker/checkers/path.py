# Copyright (c) 2009-2010 Simplistix Ltd
#
# See license.txt for more details.
from __future__ import with_statement

import os
import re
import subprocess

import execute

unix_row_re = re.compile(
    '^((?P<dirname>/.*:)|(?P<perms>[\w-][wrx-]{9}) '
    '+(?P<links>\d+) (?P<user>[\w_-]+) +(?P<group>[\w_-]+) '
    '+(?P<size>\d+) +(?P<path>.*))$',
    re.MULTILINE
    )

win_row_re = re.compile(
    '^^( +(?P<dir>Directory of .+\n ?)\n)|'
    '^(\w*\d\d/\d\d/\d{4}\W+\d\d:\d\d\W+(<DIR>|[\d,]+)\W+'
    '(?P<user>[\w\\\\]+) +'
    '(?P<path>[^\n]+)$)',
    re.MULTILINE
    )

def check(config_folder,path):
    
    output = []
    
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return "Does not exist:"+repr(path)
    
    spath = path.split(os.sep)
    target_dir = os.path.join(config_folder,*spath[1:-1])
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    tpath = os.path.join(target_dir,spath[-1])
    with open(tpath+'.listing','wb') as f:
        if subprocess.mswindows:
            if os.path.isfile(path):
                cp = 'copy'
            else:
                cp = 'xcopy /I /E /Q /H /R /Y'
            execute.simple('%s "%s" "%s"'%(cp,path,tpath))
            text = execute.simple('dir /q /s "%s"' % path)
            for e in win_row_re.finditer(
                text
                ):
                dir = e.group('dir')
                if dir:
                    print >>f
                    print >>f,dir
                    continue
                if e.group('path')=='..':
                    continue
                print >>f,\
                    e.group('user'),\
                    e.group('path')
        else:
            execute.simple('cp -R %r %r'%(path,target_dir))
            for e in unix_row_re.finditer(
                execute.simple('LC_COLLATE="C" ls -laR --time-style=+ %r'%path)
                ):
                if e.group('path')=='..':
                    continue
                if e.group('dirname'):
                    print >>f,e.group('dirname')
                else:
                    print >>f,\
                        e.group('perms'),\
                        e.group('user'),\
                        e.group('group'),\
                        e.group('path')
    return ''
