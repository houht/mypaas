#!/usr/bin/env python
# coding=utf-8

import os
import sys


#for path in [
#    os.path.join('opt', 'cattle', 'lib'),
#    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
#]:
#    if os.path.exists(os.path.join(path, 'cattle', '__init__.py')):
#        sys.path.append(path)
#        break

from cattle.server import Server
from cattle.utils import LoggerUtil

import signal
import optparse

def get_cattle_version() :
    return "1.0.0.1"
def get_help():
    return "cattled [option] strat|stop|restart"
    
def main() :
    logger = LoggerUtil().getLogger()
    try :
        # Initialize Options
        parser = optparse.OptionParser()
        parser.add_option("-c", "--configfile",
                          dest="configfile",
                          default="/etc/cattle.conf",
                          help="config file")
                          
        parser.add_option("-v", "--version",
                          dest="version",
                          default=False,
                          action="store_true",
                          help="display the version and exit")
        parser.add_option("-u", "--user",
                          dest="user",
                          default=None,
                          help="Change to specified unprivilegd user")
        parser.add_option("-g", "--group",
                          dest="group",
                          default=None,
                          help="Change to specified unprivilegd group")
        
        # Parse Command Line Args
        (options, args) = parser.parse_args()
        
        # Initial variables
        uid = -1
        gid = -1
        
        if options.version:
            print "cattle version %s" % (get_cattle_version())
            sys.exit(0)
        
        configfile = options.configfile
    # Pass the exit up stream rather then handle it as an general exception
    except SystemExit, e:
        raise SystemExit

    except Exception, e:
        import traceback
        sys.stderr.write("Unhandled exception: %s" % str(e))
        sys.stderr.write("traceback: %s" % traceback.format_exc())
        sys.exit(1)
    
    # Switch to using the logging system
    try :
        '''
        config = {}
        config['pidfile'] = '/var/run/cattle/cattle.pid'
        config['stderr'] = '/var/log/cattle/error.log'
        config['stdout'] = '/var/log/cattle/out.log'
        config['stdin'] = '/dev/null'
        if len(args) != 1 :
            print get_help()
            sys.exit(1)
        
        server = Server(config)
        if args[0] == 'start' :
            server.start()
        elif args[0] == 'stop' :
            server.stop()
        elif args[0] == 'restart' :
            server.restart()
        else :
            print get_help()
            sys.exit(1)
        # Initialize Server
        #server = Server(config)
        '''
        config = {}
        config['pidfile'] = '/var/run/cattle/cattle.pid'
        config['stderr'] = '/var/log/cattle/error.log'
        config['stdout'] = '/var/log/cattle/out.log'
        config['stdin'] = '/dev/null'
        daemon = Server(config)
        daemon.start()
        
        print 'exit'
    # Pass the exit up stream rather then handle it as an general exception
    except SystemExit, e:
        logger.error("ssssssUnhandled exception: %s" % str(e))
        raise SystemExit

    except Exception, e:
        import traceback
        logger.error("Unhandled exception: %s" % str(e))
        logger.error("traceback: %s" % traceback.format_exc())
        sys.exit(1)    
if __name__ == "__main__":
    main()
