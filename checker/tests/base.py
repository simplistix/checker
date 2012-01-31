# Copyright (c) 2009-2010 Simplistix Ltd
#
# See license.txt for more details.
from __future__ import with_statement

import atexit,os,re,sys

from checker import main
from mock import Mock
from os.path import exists
from testfixtures import compare,Comparison as C,TempDirectory
from testfixtures import LogCapture,Replacer
from unittest import TestCase

class BaseContext:

    def __init__(self,*args,**kw):
        self.r = Replacer()
        self.cleanups = [self.r.restore]
        self.setUp(*args,**kw)
        
    def __enter__(self):
        return self
    
    def __exit__(self,*args):
        for c in self.cleanups:
            c()
    
class ContextTest(TestCase):

    def setUp(self):
        self.c = self.context()

    def tearDown(self):
        self.c.__exit__()


def cleanup(path):
    # cross-platform:
    # always /-separated
    path = path.replace(os.sep,'/')
    # remove drive on windows
    path = path.split('/')
    path[0]=''        
    return '/'.join(path)
    
class OpenRaisesContext(BaseContext):

    def setUp(self,argv):
        def dummy_open(path,mode):
            raise IOError('%r %r'%(cleanup(path),mode))
        self.r.replace('sys.argv',argv)
        self.r.replace('checker.open',dummy_open,strict=False)

class DirHandlerContext(BaseContext):
    
    def setUp(self):
        self.dir = TempDirectory()
        self.cleanups.extend([self.dir.cleanup,self.removeAtExit])
        # This one is so that we can check what log handlers
        # get added.
        self.handlers = []
        self.r.replace('checker.logger.handlers',self.handlers)

    def run_with_config(self,config):
        self.dir.write('checker.txt',config)
        main(('-C '+self.dir.path).split())

    def removeAtExit(self):
        # make sure we haven't registered any atexit funcs
        atexit._exithandlers[:] = []
        
class ConfigContext(DirHandlerContext):

    def setUp(self):
        DirHandlerContext.setUp(self)
        self.checked = Mock()
        def check(config_folder,checker,param):
            getattr(self.checked,checker)(config_folder,param)
        self.r.replace('checker.check',check)

    def check_checkers_called(self,*expected):
        compare(self.checked.method_calls,list(expected))

class OutputtingContext(DirHandlerContext):

    def setUp(self):
        DirHandlerContext.setUp(self)
        def resolve(dotted):
            def the_checker(config,param):
                return dotted
            return the_checker
        self.r.replace('checker.resolve',resolve)
        
    def run_with_config(self,config):
        config+='\nreal:checker'
        self.dir.write('checker.txt',config)
        main(('-C '+self.dir.path).split())

    def check_email_config(self,from_,to_,subject,smtphost):
        compare([C('mailinglogger.SummarisingLogger',
                   mailer=C('mailinglogger.MailingLogger',
                            fromaddr=from_,
                            toaddrs=to_,
                            subject=subject,
                            mailhost=smtphost,
                            send_empty_entries=False,
                            strict=False,
                            ),
                   strict=False,
                   )],self.handlers)

# This convoluted mess is to normalise absolute paths
# to look like unix paths on both unix and windows :-/
cleaner = re.compile('('+re.escape(os.path.abspath('/'))+'\\\\?)|'+re.escape('\\')+'{1,2}')

class CommandContext(DirHandlerContext):

    def exists(self,path):
        if cleanup(path) in self.existing_paths:
            return True
        return exists(path)
    
    def setUp(self):
        DirHandlerContext.setUp(self)
        self.r.replace('execute.simple',self.simple)
        self.r.replace('execute.returncode',self.returncode)
        self.r.replace('os.path.exists',self.exists)
        self.existing_paths = set()
        self.called=[]
        self.expected={}
        self.config_folder = self.dir.path

    def run_with_config(self,config):
        with LogCapture() as output:
            with Replacer() as r:
                # This one is so that there is no output...
                r.replace('checker.StreamHandler',Mock())
                DirHandlerContext.run_with_config(self,config)
        # ...other than what we capture with the LogCapture
        self.output = output
        
    def __cleanup(self,command):
        command = cleaner.sub('/',command)
        command = command.replace(cleaner.sub('/',self.dir.path),'<config>')
        return command
        
    def __call__(self,command,cwd):
        "Where the simulated call takes place"
        command = self.__cleanup(command)
        output,files,returncode = self.expected.get(command,('',(),0))
        for path,content in files:
            self.dir.write(path.split('/'),content)
        if cwd:
            self.called.append(self.__cleanup('chdir '+cwd))
        self.called.append(command)
        return output,returncode

    def simple(self,command,cwd=None):
        return self(command,cwd)[0]

    def returncode(self,command,cwd=None):
        return self(command,cwd)[1]

    def add(self,command,output='',files=(), returncode=0):
        self.expected[command]=(output,files,returncode)

def _listall(path,dir):
    for (dirpath,dirnames,filenames) in sorted(os.walk(path)):
        if dirpath!=path and dir:
            yield dirpath
        for name in sorted(filenames):
            yield os.path.join(dirpath,name)
    
def listall(tempdir,dir=True):
    path = tempdir.path
    lpath = len(path)+1
    result = []
    for path in _listall(path,dir):
        result.append(path[lpath:].replace(os.sep,'/'))
    return result
    
