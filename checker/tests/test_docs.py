# Copyright (c) 2009-2010 Simplistix Ltd
#
# See license.txt for more details.

import re

from doctest import REPORT_NDIFF,ELLIPSIS
from glob import glob
from manuel import doctest,codeblock,capture
from manuel.testing import TestSuite as MTestSuite
from os.path import dirname,join,pardir
from unittest import TestSuite
from zc.buildout.testing import buildoutSetUp,buildoutTearDown
from zc.buildout.testing import install,install_develop
from zc.buildout.testing import normalize_endings
from zc.buildout.testing import normalize_path
from zc.buildout.testing import normalize_script
from zope.testing.renormalizing import RENormalizing

checker = RENormalizing([
        normalize_endings,
        normalize_script,
        normalize_path,
        (re.compile(
                "Couldn't find index page for '[a-zA-Z0-9.]+' "
                "\(maybe misspelled\?\)"
                "\n"
                ), ''),
        ])

def setUp(test):
    buildoutSetUp(test)
    install('zc.recipe.egg',test)
    install('argparse',test)
    install('execute',test)
    install('mailinglogger',test)
    install('zope.dottedname',test)
    install_develop('checker',test)
    
def test_suite():
    m =  doctest.Manuel(optionflags=REPORT_NDIFF|ELLIPSIS,
                        checker = checker)
    m += codeblock.Manuel()
    m += capture.Manuel()

    # overkill, but makes sure we test all files!
    buildout = []
    normal = []
    for p in glob(join(dirname(__file__),pardir,pardir,'docs','*.txt')):
        if p.endswith('installation.txt'):
            buildout.append(p)
        else:
            normal.append(p)

    s = TestSuite()
    s.addTests(MTestSuite(m,
                          setUp=setUp,
                          tearDown=buildoutTearDown,
                          *buildout))
    s.addTests(MTestSuite(m,*normal))
    return s
