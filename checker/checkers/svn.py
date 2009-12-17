# Copyright (c) 2009 Simplistix Ltd
#
# See license.txt for more details.

from cStringIO import StringIO
from subprocess import Popen,PIPE,STDOUT
import sys

def check(param):
    process = Popen('echo foo',shell=True,stderr=STDOUT,stdout=PIPE)
    print process.communicate()
