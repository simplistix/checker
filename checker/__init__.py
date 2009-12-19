# Copyright (c) 2009 Simplistix Ltd
#
# See license.txt for more details.

import argparse
import os
import sys

from logging import getLogger,StreamHandler,INFO
from mailinglogger.SummarisingLogger import SummarisingLogger
from zope.dottedname.resolve import resolve

logger = getLogger()

def check(config_folder,checker,param):
    output = resolve('checker.checkers.%s.check'%checker)(
        config_folder,
        param
        )
    if output.endswith('\n'):
        output = output[:-1]
    if output:
        logger.info(output)
        
special = (
    'config_checker',
    'email_to',
    'email_from',
    'email_subject',
    'email_smtphost',
    )

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-C',default='/config',dest='config_folder')
    args = parser.parse_args(argv)
    args.config_checker = 'svn'
    args.config_folder = os.path.abspath(args.config_folder)
    checkers = []
    for line in open(os.path.join(args.config_folder,'checker.txt'),'rU'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue
        c = line.split(':',1)
        if len(c)!=2:
            raise ValueError('No colon found on a line in checker.txt')
        if c[0] in special:
            setattr(args,c[0],c[1])
        else:
            checkers.append(c)
    logger.setLevel(INFO)
    if getattr(args,'email_to',None):
        to_ = [e.strip() for e in args.email_to.split(',')]
        from_ = getattr(args,'email_from',to_[0]).strip()
        handler = SummarisingLogger(
            from_,to_,
            subject=getattr(args,'email_subject',
                            'Checker output from %(hostname)s').strip(),
            mailhost=getattr(args,'email_smtphost','localhost').strip(),
            send_empty_entries=False,
            )
    else:
        handler = StreamHandler(sys.stdout)
    logger.addHandler(handler)
    for c in checkers:
        check(args.config_folder,*c)
    for checker in args.config_checker.split(','):
        check(args.config_folder,checker,args.config_folder)
