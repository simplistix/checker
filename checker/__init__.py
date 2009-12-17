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
    check(args.config_folder,args.config_checker,args.config_folder)

# old below here
import re
import shutil
import sys

svn = '/usr/bin/svn '
config = '/config'

# break a row into groups
row_re = re.compile('^((?P<dirname>/.*:)|(?P<perms>[\w-][wrx-]{9}) +(?P<links>\d+) (?P<user>[\w_-]+) +(?P<group>[\w_-]+) +(?P<size>\d+) +(?P<path>.*))$',
                    re.MULTILINE)
# remove svn:externals crap
svnexternal_re = re.compile("(^X.*\n)|(\nPerforming status on external item at '.*')\n",
                            re.MULTILINE)

def svn_status(path):
    o = os.popen(svn+'status '+path).read()
    o = svnexternal_re.sub('',o)
    sys.stdout.write(o)

def svn_up_and_status(path):
    os.system(svn+'up -q '+path)
    svn_status(path)

def old_main():
    # make sure we have the latest config
    os.system(svn+' up -q '+config)

    for line in open(config+'/checker.txt','rU'):
        line = line.strip()
        if ':' in line:
            prefix,path = line.split(':')
        else:
            prefix,path = None,line
        if prefix=='crontab':
            os.system(('crontab -u %s -l > '+config+'/crontabs/%s') % (path,path))
        elif prefix=='svn':
            svn_up_and_status(path)
        elif prefix=='buildout':
            svn_up_and_status(path)
            cwd = os.getcwd()
            os.chdir(path)
            os.system('bin/buildout -o -q')
            os.chdir(cwd)
        elif path and path[0]=='/':
            if not os.path.exists(path):
                print "Does not exist:",repr(path)
            dir,element = os.path.split(path)
            target_dir = config+dir
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            os.system('cp -R '+path+' '+target_dir)
            target_path = target_dir+'/'+element
            ls_path = target_path+'.ls'
            os.system('ls -laR --time-style=+ '+path+' >'+ls_path)
            f = open(ls_path)
            text = f.read()
            f.close()
            f = open(ls_path,'w')
            for e in row_re.finditer(text):
                if e.group('path')=='..':
                    continue
                if e.group('dirname'):
                    print >>f,e.group('dirname')
                else:
                    print >>f,e.group('perms'),e.group('user'),e.group('group'),e.group('path')
            f.close()

    svn_status(config)
