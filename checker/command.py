# Copyright (c) 2009 Simplistix Ltd
#
# See license.txt for more details.

from subprocess import Popen,PIPE,STDOUT

def execute(command,cwd=None):
    return Popen(
        command,
        stderr=STDOUT,
        stdout=PIPE,
        universal_newlines=True,
        cwd=cwd,
        shell=True,
        ).communicate()[0]
