#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************
import re
import os
import itertools  


from command import Command
from customException import CustomException


class LvmDriver:
    "Driver for Linux servers running LVM.."

    
    def __init__(self,vg_name):
        self.cmd = Command()
        self.vg_name = vg_name
    
    
    def vg_exists(self):
        """Simple check to see if VG exists.
        :returns: True if vg specified in object exists, else False
        """
        
        exists = False
        out = self.cmd.execute('env', 'LC_ALL=C', 'vgs', '--noheadings', '-o', 'name',self.vg_name)
        
        if out is not None:
            volume_groups = out.split("\n")
            if self.vg_name in volume_groups:
                exists = True

        return exists

    

    def create_vg(self,vg_name, pv_list):
        "Create volume group."
        try:
            self.cmd.execute('vgcreate', self.vg_name, ' '.join(pv_list))
        except Exception , e:
            raise CustomException("Error: %s" % str(e) ) 
    
    
    
    def vg_size(self):
        "Return: vg totle_size ;vg free_size"
        
        try:
            out = self.cmd.execute("vgs | grep %s | awk {'print $6,$7'} " % self.vg_name)
        except Exception , e:
            raise CustomException("Error: %s" % str(e) ) 
     
        if out is not None:
            size = out.split(" ")
        
        return size
    
    def rename_volume(self, lv_name, new_name):
        "Change the name of an existing volume."
        
        try:
            self.cmd.execute('lvrename', self.vg_name, lv_name, new_name)
        except Exception , e:
            raise CustomException("Error: %s" % str(e) ) 


    def create_volume(self, name, size):
        """Creates a logical volume on the object's VG.
        param name: Name to use when creating Logical Volume
        param size: Size to use when creating Logical Volume
        """
        
        try:
            self.cmd.execute('lvcreate', '-n', name, self.vg_name, '-L', size)
        except Exception , e:
            raise CustomException("Error: %s" % str(e) ) 
        
    
    def remove_volume(self, lv_dir):
        """Creates a logical volume on the object's VG.
        param lv_dir: Name to lv dir
        """
        
        try:
            self.cmd.execute('lvremove', '-f',lv_dir)
        except Exception , e:
            raise CustomException("Error: %s" % str(e) )
            
    def extend_volume(self, lv_name, new_size):
        "Extend the size of an existing volume."
        
        try:
            self.cmd.execute('lvextend', '-L', new_size,
                          '%s/%s' % (self.vg_name, lv_name),)
        except Exception , e:
            raise CustomException("Error: %s" % str(e) )


    def get_lvm_version(self):
        """Static method to get LVM version from system.

        :param root_helper: root_helper to use for execute
        :returns: version 3-tuple

        """
        
        try:
            out = self.cmd.execute('env', 'LC_ALL=C', 'vgs', '--version')
        except Exception , e:
            raise CustomException("Error: %s" % str(e) )
            
        lines = out.split('\n')
        
        for line in lines:
            if 'LVM version' in line:
                version_list = line.split()
                version = version_list[2]
                return version

    def get_lvm_path(self,lv_name):
        """Static method to get LVM version from system.

        :param root_helper: root_helper to use for execute
        :returns: lvm path

        """
        
        try:
            cmd = ('lvdisplay | grep "LV Path" | grep %s | awk %s'%(lv_name+'$',' \'{print $3}\' '))
            out = os.popen(cmd,'r').readline()
            #out = self.cmd.execute('lvdisplay | grep "LV Path" | grep %s | awk %s'%(lv_name+'$',' \'{print $3}\' '))
        except Exception , e:
            raise CustomException("Error: %s" % str(e) )
        
        path = out.rstrip("\n")
        return path


    def get_all_volumes(self,vg_name=None):
        """Static method to get all LV's on a system.
        
        :param vg_name: optional, gathers info for only the specified VG
        :returns: List of Dictionaries with LV info

        """
        try:
            if vg_name is not None:
                out = self.cmd.execute('env', 'LC_ALL=C', 'lvs', '--noheadings', '--unit=g', '-o', 'vg_name,name,size', '--nosuffix',vg_name)
            else:
                out = self.cmd.execute('env', 'LC_ALL=C', 'lvs', '--noheadings', '--unit=g', '-o', 'vg_name,name,size', '--nosuffix')
        except Exception , e:
            raise CustomException("Error: %s" % str(e) )
       
        
        lv_list = []
        if out is not None:
            volumes = out.split()
            for vg, name, size in itertools.izip(*[iter(volumes)] * 3):
                lv_list.append({"vg": vg, "name": name, "size": size})

        return lv_list 


    def get_volumes(self):
        """Get all LV's associated with this instantiation (VG).

        :returns: List of Dictionaries with LV info

        """
        
        lv_list = self.get_all_volumes(self.vg_name)
        return lv_list
        

    def get_volume(self, name):
        """Get reference object of volume specified by name.

        :returns: dict representation of Logical Volume if exists

        """
        ref_list = self.get_volumes()
        for r in ref_list:
            if r['name'] == name:
                return r
       
    def get_all_physical_volumes(self,vg_name=None):
        """Static method to get all PVs on a system.

        :param root_helper: root_helper to use for execute
        :param vg_name: optional, gathers info for only the specified VG
        :returns: List of Dictionaries with PV info

        """

        
        try:
            out = self.cmd.execute('env', 'LC_ALL=C', 'pvs', '--noheadings',
               '--unit=g',
               '-o', 'vg_name,name,size,free',
               '--separator', ':',
               '--nosuffix')
        except Exception , e:
            raise CustomException("Error: %s" % str(e) )

        pvs = out.split()
        if vg_name is not None:
            pvs = [pv for pv in pvs if vg_name == pv.split(':')[0]]

        pv_list = []
        for pv in pvs:
            fields = pv.split(':')
            pv_list.append({'vg': fields[0],
                            'name': fields[1],
                            'size': float(fields[2]),
                            'available': float(fields[3])})
        return pv_list
        
        
    def get_physical_volumes(self):
        """Get all PVs associated with this instantiation (VG).

        :returns: List of Dictionaries with PV info

        """
        pv_list = self.get_all_physical_volumes( self.vg_name)
        return pv_list
           
           
    def get_all_volume_groups(self, vg_name=None):
        """Static method to get all VGs on a system.

        :param vg_name: optional, gathers info for only the specified VG
        :returns: List of Dictionaries with VG info

        """

        try:
            if vg_name is not None:
                out = self.cmd.execute('env', 'LC_ALL=C', 'vgs', '--noheadings', '--unit=g',
                   '-o', 'name,size,free,lv_count,uuid', '--separator', ':',
                   '--nosuffix',vg_name)
            else:
                out = self.cmd.execute('env', 'LC_ALL=C', 'vgs', '--noheadings', '--unit=g',
                   '-o', 'name,size,free,lv_count,uuid', '--separator', ':',
                   '--nosuffix')
        except Exception , e:
            raise CustomException("Error: %s" % str(e) )


        vg_list = []
        if out is not None:
            vgs = out.split()
            for vg in vgs:
                fields = vg.split(':')
                vg_list.append({'name': fields[0],
                                'size': float(fields[1]),
                                'available': float(fields[2]),
                                'lv_count': int(fields[3]),
                                'uuid': fields[4]})

        return vg_list    
        
        
