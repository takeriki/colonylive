#!/usr/bin/env python2
# -*- coding:utf-8 -*-


"""
Configuration manager

"""

import os
from os.path import expanduser
import ConfigParser

path = os.path.dirname(os.path.abspath(__file__))
fpath = path + '/../../colonylive.cfg'
#home = expanduser("~")
#fpath = home + '/colonylive/colonylive.cfg'

cfg = ConfigParser.SafeConfigParser()


class Configure():
    """
    colonyliveの設定を読み込む

    """

    def __init__(self):
        self.load()

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):
        return str(self.__dict__)

    def load(self):
        cfg.read(fpath)
        for section in cfg.sections():
            for option in cfg.options(section):
                key = (section, option)
                value = cfg.get(section, option)
                self.__dict__[key] = value
    
    def update(self):
        for key, value in self.__dict__.items():
            section, option = key
            try:
                cfg.set(section, option, value)
            except ConfigParser.NoSectionError:
                cfg.add_section(section)
                cfg.set(section, option, value)
            except Exception as e:
                print e.message
                quit()

        f = open(fpath,'w')
        cfg.write(f)
        f.close()
    
    
    def check(self):
        for key, value in self.__dict__.items():
            if value == "":
                print "Section [%s] Option [%s]: no value" % key
                quit()


    def set_default(self):
        sets = [
        (('admin','name'),'admin'),
        (('admin','email'),'admin@host.com'),
        (('db','host'),'localhost'),
        (('db','db'),'clive1'),
        (('db','user'),'clive'),
        (('db','pass'),'colonylive'),
        (('db','port'),'3306'),
        (('folder','img_tmp'),'%s/img_tmp/' % home),
        (('folder','img_scan'),'%s/img_scan/' % home),
        (('folder','img_store'),'%s/img/' % home),
        (('scan','scanner_ids'),''),
        (('scan','min_cycle'),'30'),
        (('scan','days_scan_keep'),'30'),
        (('colony','r_center_mass'),'8'),
        (('growth','od_limit'),'1'),
        (('growth','point_number_use'),'100'),
        (('growth','frac_limit_ip'),'0.8'),
        (('growth','min_fixed_time_point'),'1200'),
        (('vuescan','pos_input_tab'),''),
        (('vuescan','pos_source'),''),
        (('vuescan','pos_mode'),''),
        (('vuescan','pos_abort'),''),
        (('vuescan','sec_scan_wait'),'240'),
        (('setup','step'),'0')
        ]
        
        for key, value in sets:
            self.__dict__[key] = value
        self.update()


if __name__ == "__main__":
    conf = Configure()
