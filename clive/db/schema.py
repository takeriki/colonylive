"""
Database schema for SQLAlchemy

"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, Float, String, DateTime, MetaData, ForeignKey

Base = declarative_base()
class Scanner(Base):
    __tablename__ = 'scanner'

    id = Column(Integer, primary_key=True)
    person_name = Column(String)
    dt_start = Column(DateTime)
    dt_finish = Column(DateTime)
    exp_ids = Column(String)
    min_grows = Column(String)
    
    def __init__(self, person_id, dt_start, dt_finish, exp_ids):
        self.person_name = person_name
        self.dt_start = dt_start
        self.dt_finish = dt_finish
        self.exp_ids = exp_ids

    def __repr__(self):
        return "ScannerID=%d" % self.id


class Imgscan(Base):
    __tablename__ = 'img_scan'

    id = Column(Integer, primary_key=True)
    dt_scan = Column(DateTime)
    scanner_id = Column(DateTime)
    exp_ids = Column(String)
    
    def __init__(self, scanner_id, dt_scan, exp_ids):
        self.scanner_id = scanner_id
        self.dt_scan = dt_scan
        self.exp_ids = exp_ids

    def __repr__(self):
        return "ImgscanID=%d" % self.id


class Img(Base):
    __tablename__ = 'img'

    id = Column(Integer, primary_key=True)
    exp_id = Column(Integer)
    scanner_id = Column(Integer)
    min_grows = Column(String)
    
    def __init__(self, exp_id, scanner_id, min_grows):
        self.exp_id = exp_id
        self.scanner_id = scanner_id
        self.min_grows = min_grows

    def __repr__(self):
        return "ImgID=%d" % self.id


class Exp(Base):
    __tablename__ = 'exp'

    id = Column(Integer, primary_key=True)
    project = Column(String)
    plate_id = Column(Integer)
    person_id = Column(Integer)
    medium = Column(String)
    conditions = Column(String)
    h_scan = Column(Integer)
    dt_start = Column(DateTime)
    pos_scan = Column(String)
    step_done = Column(Integer)
    n_death = Column(Integer)
    pcc = Column(Float)
    failure = Column(String)
    note = Column(String)
    in_process = Column(Integer)
    
    def __init__(self, person_id, project, plate_id, medium, dt_start, conditions, h_scan, pos_scan):
        self.person_id = person_id
        self.project = project
        self.plate_id = plate_id
        self.medium = medium
        self.dt_start = dt_start
        self.conditions = conditions
        self.h_scan = h_scan
        self.pos_scan = pos_scan
        self.step_done = 0
        self.in_process = 0

    def __repr__(self):
        return "ExpID=%d" % self.id


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    user = Column(Integer)
    pass_sha1 = Column(String)
    name = Column(String)
    email = Column(String)
    
    def __init__(self, user, pass_sha1, name, email):
        self.user = user
        self.pass_sha1 = pass_sha1
        self.name = name
        self.email = email

    def __repr__(self):
        return "PersonID=%d" % self.id


class Plate(Base):
    __tablename__ = 'plate'

    id = Column(Integer, primary_key=True)
    ncol = Column(Integer)
    nrow = Column(Integer)
    name = Column(String)
    
    def __init__(self, ncol, nrow, name):
        self.ncol = ncol
        self.nrow = nrow
        self.name = name

    def __repr__(self):
        return "PlateID=%d" % self.id



class Colony(Base):
    __tablename__ = 'colony'

    id = Column(Integer, primary_key=True)
    exp_id = Column(Integer)
    col = Column(Integer)
    row = Column(Integer)
    location = Column(String)
    areas = Column(String)
    masss = Column(String)
    cmasss = Column(String)
    
    def __init__(self, exp_id, col, row, location, areas, masss, cmasss):
        self.exp_id = exp_id
        self.col = col
        self.row = row
        self.location = location
        self.areas = areas
        self.masss = masss
        self.cmasss = cmasss

    def __repr__(self):
        return "ColonyID=%d" % self.id


class Growth(Base):
    __tablename__ = 'growth'

    id = Column(Integer, primary_key=True)
    exp_id = Column(Integer)
    col = Column(Integer)
    row = Column(Integer)
    con = Column(Integer)
    ltg = Column(Float)
    mgr = Column(Float)
    spg = Column(Float)
    
    def __init__(self, exp_id, col, row, con, ltg, mgr, spg):
        self.exp_id = exp_id
        self.col = col
        self.row = row
        self.con = con
        self.ltg = ltg
        self.mgr = mgr
        self.spg = spg

    def __repr__(self):
        return "GrowthID=%d" % self.id


class GrowthRaw(Base):
    __tablename__ = 'growth_raw'

    id = Column(Integer, primary_key=True)
    exp_id = Column(Integer)
    col = Column(Integer)
    row = Column(Integer)
    con = Column(Integer)
    ltg = Column(Float)
    mgr = Column(Float)
    spg = Column(Float)
    
    def __init__(self, exp_id, col, row, con, ltg, mgr, spg):
        self.exp_id = exp_id
        self.col = col
        self.row = row
        self.con = con
        self.ltg = ltg
        self.mgr = mgr
        self.spg = spg

    def __repr__(self):
        return "GrowthRawID=%d" % self.id


