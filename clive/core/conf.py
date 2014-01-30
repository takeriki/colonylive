"""
Configuration manager

"""


from os.path import expanduser
import ConfigParser

home = expanduser("~")
fpath = home + '/clive.cfg'
cfg = ConfigParser.SafeConfigParser()


class Configure():
    def __init__(self):
        self._load()

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):
        return str(self.__dict__)

    def _load(self):
        cfg.read(fpath)
        for section in cfg.sections():
            for option in cfg.options(section):
                key = (section, option)
                value = cfg.get(section, option)
                self.__dict__[key] = value
    
    def update(self):
        for key, value in self.__dict__.items():
            section, option = key
            cfg.set(section, option, value)
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
        (('admin','name'),''),
        (('admin','email'),''),

        (('db','main'),''),

        (('folder','img_tmp'),'%s/img_tmp/' % home),
        (('folder','img_scan'),'%s/img_scan/' % home),
        (('folder','img_scan'),'%s/img/' % home),

        (('scan','scanner_ids'),''),
        (('scan','pos_scan'),''),
        (('scan','min_cycle'),'30'),
        (('scan','days_scan_keep'),'30'),

        (('pixel','plate_horizontal'),'1900'),
        (('pixel','plate_vertical'),'1320'),

        (('vuescan','pos_input_tab'),''),
        (('vuescan','pos_source'),''),
        (('vuescan','pos_mode'),''),
        (('vuescan','pos_abort'),''),
        (('vuescan','sec_scan_wait'),'240')
        ]
        
        for key, value in sets:
            self.__dict__[key] = value
        self.update()


if __name__ == "__main__":
    conf = Configure()
