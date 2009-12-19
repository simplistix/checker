# Copyright (c) 2009 Simplistix Ltd
#
# See license.txt for more details.

from checker import command
from re import compile,MULTILINE

svnexternal_re = compile(
    "(^X.*\n)|(\nPerforming status on external item at '.*')\n",
    MULTILINE
    )

def check(config_folder,path):    
    command.execute('svn up -q '+path)
    return svnexternal_re.sub('',command.execute('svn status '+path))
