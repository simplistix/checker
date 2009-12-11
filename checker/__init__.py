#!/usr/bin/python
import os
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

def main():
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
