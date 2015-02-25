#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************

from subprocess import Popen,PIPE,STDOUT


from customException import CustomException


class Command:
    "linux executer."
    
    def __init__(self):
        pass
    
    def execute(self,*popenargs, **kwargs):
        "Helper method to shell out and execute a command through subprocess."
        
        """Run command with arguments and return its output as a byte string.
    
        If the exit code was non-zero it raises a CalledProcessError.  The
        CalledProcessError object will have the return code in the returncode
        attribute and output in the output attribute.
    
        The arguments are the same as for the Popen constructor.  Example:
    
        >>> check_output(["ls", "-l", "/dev/null"])
        'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'
    
        The stdout argument is not allowed as it is used internally.
        To capture standard error in the result, use stderr=STDOUT.
    
        >>> check_output(["/bin/sh", "-c",
        ...               "ls -l non_existent_file ; exit 0"],
        ...              stderr=STDOUT)
        'ls: non_existent_file: No such file or directory\n'
        """
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        
        
        process = Popen((' '.join(popenargs)), shell = True, stdout = PIPE, stderr = STDOUT, **kwargs) 
        
        output, unused_err = process.communicate()
        
        retcode = process.poll()
        
        #if retcode:
        #    raise CustomException("%s,%s" % (retcode,output))
        
        return output.strip() 
        