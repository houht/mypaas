import logging.config
from logging.handlers import RotatingFileHandler
import os.path
from cattle.utils import ParserConf

class LoggerUtil() :
    
#    def __new__(cls, *args, **kw):  
#        if not cls.__instance:
#            cls.__instance = super(LoggerUtil, cls).__new__(cls, *args, **kwargs)
#        return cls.__instance
    logger = None    
    def __init__(self, config = "/etc/koala/koala.conf") :
        '''
        #这里来设置日志的级别
        #CRITICAl    50
        #ERROR    40
        #WARNING    30
        #INFO    20
        #DEBUG    10
        #NOSET    0
        #写入日志时，小于指定级别的信息将被忽略
        '''
        #global logger
        
        if LoggerUtil.logger == None :
            #logpath=None, level=30,format='%(asctime)s %(levelname)s %(filename)s[line:%(lineno)d]: %(message)s',maxbytes=104857600,backupcount=5
            conf = ParserConf(config)
            level = conf.get_item('LOG', 'level')
            format = conf.get_item('LOG', 'format')
            maxbytes = conf.get_item('LOG', 'maxbytes')
            backupcount = conf.get_item('LOG', 'backupcount')
            logpath = conf.get_item('LOG', 'logpath')
            filter = conf.get_item('LOG', 'filter')
                        
            if level == None :
                level = 30
            else :
                level = int(level)
            if format == None :
                format = '%(asctime)s %(levelname)s %(filename)s[line:%(lineno)d]: %(message)s'
            if maxbytes == None :
                maxbytes = 10485760
            else :
                maxbytes = int(maxbytes)            
            if backupcount == None :
                backupcount = 5
            else :
                backupcount = int(backupcount) 
            if logpath == None :
                logpath = "/var/log/koala/koala.log"       
            LoggerUtil.logger = logging.getLogger(logpath)
            
            if os.path.exists(os.path.dirname(logpath)) == False :
                os.makedirs(os.path.dirname(logpath))
                
            #print conf,level,maxbytes,backupcount,logpath,format
            LoggerUtil.logger.setLevel(level)
            Rthandler = RotatingFileHandler(logpath, maxBytes=maxbytes, backupCount=backupcount)
            formatter = logging.Formatter(format)
            Rthandler.setFormatter(formatter)
            LoggerUtil.logger.addHandler(Rthandler)
            if filter != None :
                LoggerUtil.logger.addFilter(filter)
    
    def getLogger(self):
        return LoggerUtil.logger
#        
#    def debug(self, msg) :
#        self.logger.debug(msg)
#    
#    def info(self, msg) :
#        self.logger.info(msg)
#    
#    def warning(self, msg) :
#        self.logger.warning(msg)
#    
#    def error(self, msg) :
#        self.logger.error(msg)
#    
#    def critical(self, msg) :
#        self.logger.critical(msg)
