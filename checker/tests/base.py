# Copyright (c) 2009 Simplistix Ltd
#
# See license.txt for more details.

import atexit,os,sys

from checker import main
from mock import Mock
# from functools import partial
from testfixtures import compare,Comparison as C,TempDirectory,Replacer

class BaseContext:

    def setUp(self):
        pass
    
    def __init__(self,*args,**kw):
        self.r = Replacer()
        self.cleanups = [self.r.restore]
        self.setUp(*args,**kw)
        
    def __enter__(self):
        return self
    
    def __exit__(self,*args):
        for c in self.cleanups:
            c()
    
class OpenRaisesContext(BaseContext):

    def setUp(self,argv):
        def dummy_open(path,mode):
            raise IOError('%r %r'%(path.replace(os.sep,'/'),mode))
        self.r.replace('sys.argv',argv)
        self.r.replace('checker.open',dummy_open,strict=False)

class DirLoggerContext(BaseContext):
    
    def setUp(self):
        self.dir = TempDirectory()
        self.cleanups.extend([self.dir.cleanup,self.removeAtExit])
        self.handlers = []
        self.r.replace('checker.logger.handlers',self.handlers)

    def removeAtExit(self):
        # make sure we haven't registered any atexit funcs
        atexit._exithandlers[:] = []
        
class ConfigContext(DirLoggerContext):

    def setUp(self):
        DirLoggerContext.setUp(self)
        self.checked = Mock()
        def check(checker,param):
            getattr(self.checked,checker)(param)
        self.r.replace('checker.check',check)

    def run_with_config(self,config):
        self.dir.write('checker.txt',config)
        main(('-C '+self.dir.path).split())

    def check_checkers_called(self,*expected):
        compare(self.checked.method_calls,list(expected))

class OutputtingContext(DirLoggerContext):

    def setUp(self):
        DirLoggerContext.setUp(self)
        def resolve(dotted):
            def the_checker(param):
                print 'stdout',dotted
                print >>sys.stderr, 'stderr',dotted
            return the_checker
        self.r.replace('checker.resolve',resolve)
        
    def run_with_config(self,config):
        config+='\nreal:checker'
        self.dir.write('checker.txt',config)
        main(('-C '+self.dir.path).split())

    def check_email_config(self,from_,to_,subject,smtphost):
        compare([C('mailinglogger.SummarisingLogger.SummarisingLogger',
                   mailer=C('mailinglogger.MailingLogger.MailingLogger',
                            fromaddr=from_,
                            toaddrs=to_,
                            subject=subject,
                            mailhost=smtphost,
                            send_empty_entries=False,
                            strict=False,
                            ),
                   strict=False,
                   )],self.handlers)

# old!
from unittest import TestCase
import logging

j = os.path.join

class runCommand:

    def __init__(self,var):
        self.responses = {}
        self.effects = {}
        self.command_to_tag = {}
        self.called=[]
        self.var = var

    def add(self,command,response='',effect=None):
        self.responses[command]=response
        if effect:
            self.effects[command]=effect
        return command
            
    def __call__(self,command,log=True):
        r = self.responses.get(command,'')
        e = self.effects.get(command)
        if e: e()
        self.called.append((command,log))
        return r

    # helpers

    def write_files(self,*sets):
        for path,content in sets:
            dirpath = path[:-1]
            if dirpath:
                dirpath = os.path.join(*dirpath)
                if not os.path.exists(dirpath):
                    os.makedirs(dirpath)
            f = open(os.path.join(*path),'wb')
            f.write(content)
            f.close()
            
    def wget(self,day,user,passwd,url,*sets):
        
        wget = (
            'wget -m -k -K -a '+j(self.var.path,'wget-'+user+'-'+day+'.log')+
            ' -nv -x -E --http-user=%s --http-passwd=%s %s'
            )%(user,passwd,url)

        self.add(wget,effect=partial(self.write_files,*sets))

        return wget
    
    def unzip(self,date,user,passwd,*sets):
        # sets should be the same as those passed to wget!
        basepath = (self.var.path,'www','static',user)
        unzip = (
            'unzip -q -o -P %s -d '+j(*basepath)+' '+
            j(self.var.path,'www',user,date+'.zip')
            ) % (passwd,)

        nsets = []
        for path,content in sets:
            nsets.append((basepath+path[1:],content))
                         
        self.add(unzip,effect=partial(self.write_files,*nsets))
        
        return unzip

    def diff(self,user,path,response=''):
        diff = (
            'diff -q '+j(self.var.path,'www','static',user,*path)+' '
            +j(self.var.path,'create',user,'premier.screendigest.com',*path)
            )
        self.add(diff,response=response)
        return diff

    def print_cwd(self,name):
        print name,':',os.getcwd()
        
    def cwd(self,name,command):
        # handy for debugging!
        self.add(command,effect=partial(self.print_cwd,name))
        
logger = logging.getLogger()

class BaseTestCase(TestCase):

    def setUp(self):        
        self.e = EnvironmentModule(False)
        self.e.install()
        self.var = TempDirectory()
        self.r = Replacer(replace_returns=True)
        self.setuplogging_setup = self.r.replace('setuplogging.setup',Mock())
        self.handlers = self.r.replace('tests.base.logger.handlers',[])
        self.command = r = runCommand(self.var)
        self.r.replace('handlers.runCommand',r)
        self.r.replace('steps.runCommand',r)
        self.r.replace('process.datetime',test_datetime())
        self.log = LogCapture()
        self.e.var_path = self.var.path
        self.e.lockfile_path = os.path.join(self.var.path,'staticsite.lock')
        self.e.full_copy_path=os.path.join(self.var.path,'fullcopy.txt')
        self.e.site_domain = 'premier.screendigest.com'
        self.e.site_url = 'http://'+self.e.site_domain
        self.e.bad_phrases = ('a bad phrase',)
        self.e.dry_run = False

        self.day = time.strftime('%a')
        self.date = time.strftime('%Y%m%d')

    def tearDown(self):
        LogCapture.uninstall_all()
        self.r.restore()
        TempDirectory.cleanup_all()
        try:
            self.e.uninstall()
        except KeyError:
            # already uninstalled!
            pass
        
    def do_run(self,raise_on_critical=True):
        # we do it this way to make sure that the
        # default is correct!
        args = []
        if raise_on_critical:
            args.append(True)
        
        main(*args)
            
        compare(self.handlers,
                [C('testfixtures.LogCapture'),
                 C('errorhandler.ErrorHandler',
                   logger='',
                   level=logging.ERROR,
                   strict=False)])
        
        compare(self.setuplogging_setup.call_args,((),{},))
