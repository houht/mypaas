# Copyright (C) 2014-2099 
#
# This file is part of cattle.
#


import sys

if sys.version_info < (2, 6):
    raise RuntimeError('You need python 2.6 for this module.')

__author__ = "zhengqs <501917150@qq.com>"
__date__ = "15 Oct 2014"
__version__ = "1.0.1 ()"
__version_info__ = (1, 0, 1)
__license__ = "Private License"

from configure.configManage import ConfigManage
from storage.storageManage import StorageManage
from network.networkManage import NetworkService
from images.imageManage import ImageManage
from virtualization.vmManage import VmManage
from application.appManage import AppManage
from application.appEnvironment import AppEnv

# fix module names for epydoc
'''for c in locals().values():
    if issubclass(type(c), type) or type(c).__name__ == 'classobj':
        # classobj for exceptions :/
        c.__module__ = __name__
del c
'''
__all__ = [ 'ConfigManage',
            'StorageManage',            
            'NetworkService',
            'ImageManage',
            'VmManage',
            'AppManage',
            'AppEnv'
           ]

