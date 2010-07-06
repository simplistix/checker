# Copyright (c) 2009-2010 Simplistix Ltd
#
# See license.txt for more details.

import execute
from re import compile,MULTILINE

svnexternal_re = compile(
    "(^X.*\n)|(\nPerforming status on external item at '.*')\n",
    MULTILINE
    )

def check(config_folder,path):    
    execute.simple('svn up -q '+path)
    return svnexternal_re.sub('',execute.simple('svn status '+path))
