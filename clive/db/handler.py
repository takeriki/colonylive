#!/usr/bin/python

import datetime
from sqlalchemy import and_, or_, distinct

from database import DB
from schema import Scanner, Imgscan, Img, Exp, Person, Plate, Growth, GrowthRaw, Colony


class ScannerHandler():
    db = DB()
    scanners = []
    
    def load(self, id):
        scanner = self.db.session.query(Scanner).get(id)
        self.db.session.refresh(scanner)
        return scanner
    
    def get_scanner_ids(self):
        query = self.db.session.query(Scanner).order_by(Scanner.id)
        return [i.id for i in query.all()]

    def update(self):
        self.db.session.commit()

    def clean(self, scanner):
        scanner.person_name = None
        scanner.dt_start = None
        scanner.dt_finish = None
        scanner.exp_ids = None
        scanner.min_grows = None
        self.db.session.commit()


class ImgscanHandler():
    db = DB()

    def load(self, id):
        return self.db.session.query(Scanimg).get(id)

    def create(self, scanner_id, exp_ids):
        img_scan = Imgscan(
            dt_scan=datetime.datetime.now(),
            scanner_id=scanner_id,
            exp_ids=exp_ids
            )
        #self._before_commit(img_scan)
        self.db.session.add(img_scan)
        self.db.session.commit()
        return img_scan
    
    def _before_commit(self, scanimg):
        tmp = scanimg.exp_ids
        scanimg.exp_ids = "|".join(map(str,tmp))

    def commit(self):
        self.db.session.commit()


class ImgHandler():
    db = DB()
    
    def load(self, id):
        return self.db.session.query(Img).get(id)

    def create(self, exp_id, scanner_id, min_grows):
        img = Img(
            exp_id=exp_id,
            scanner_id=scanner_id,
            min_grows=min_grows
            )
        self.db.session.add(img)
        self.db.session.commit()
        return img
    """ 
    def get_imgs_by_expid(self, exp_id):
        return self.db.session.query(Img).filter(
            Img.exp_id == exp_id
            ).order_by(Img.min_grows).all()
    """ 
    def load_by_expid(self, exp_id):
        return self.db.session.query(Img).filter(
            Img.exp_id == exp_id).one()


class ExpHandler():
    db = DB()
    
    def create(self, person_id, project, plate_id, medium, dt_start, conditions, h_scan, pos_scan):
        exp = Exp(
            person_id=person_id,
            project=project,
            plate_id=plate_id,
            medium=medium,
            dt_start=dt_start,
            conditions=conditions,
            h_scan=h_scan,
            pos_scan=pos_scan
            )
        self.db.session.add(exp)
        self.db.session.commit()
        return exp

    def load(self, id):
        return self.db.session.query(Exp).get(id)
    
    def find_exps_by_dt_plan(self, dt_start, dt_end):
        return self.db.session.query(Exp)\
            .filter(and_(
            Exp.dt_start > dt_start,
            Exp.dt_start < dt_end
            )).all()
    
    def get_reserved_exps_in_person(self):
        return self.db.session.query(Exp).filter(
            or_(
            Exp.step_done == 0,
            Exp.in_process == 1,
            )).order_by(Exp.dt_start).all()
    
    def get_reserved_exps(self):
        return self.db.session.query(Exp).filter(
            Exp.step_done == 0
            ).order_by(Exp.dt_start).all()

    def get_future_personal_exps(self, person_id):
        dt_now=datetime.datetime.now()
        return self.db.session.query(Exp).filter(
            and_(
            Exp.person_id == person_id,
            Exp.dt_start > dt_now
            )).all()
    
    def get_unprocess_exps(self):
        return self.db.session.query(Exp).filter(
            and_(
            Exp.step_done < 4,
            Exp.in_process == 0,
            Exp.failure == None
            )).all()
    
    def remove(self, exp):
        self.db.session.delete(exp)
        self.db.session.commit()

    def update(self):
        self.db.session.commit()

    def get_growth_ary(self, id, item='mgr'):
        exp = self.db.session.query(Exp).get(id)
        
        sql = "SELECT col, row, %s FROM growth WHERE exp_id=%d" % (item, self.ind)
        CUR.execute(sql)
        res = CUR.fetchall()
        ary = self.plate.gary.copy()
        if len(res) != ary.size:
            print "Error: Data number mismatch."
            print "Expect=%d,  Actural=%d" % (ary.size,len(res))
            quit()
        for items in res:
            col, row, v = items
            ary[row-1, col-1] = v
        #ary = np.ma.masked_array(ary, ary==0)
        return ary


class PersonHandler():
    db = DB()

    def load(self, id):
        return self.db.session.query(Person).get(id)
    
    def create(self, user, pass_sha1, name, email):
        person = Person(
            user = user,
            pass_sha1 = pass_sha1,
            name = name,
            email = email
            )
        self.db.session.add(person)
        self.db.session.commit()
        return person

    def authenticate(self, user, pass_sha1):
        return self.db.session.query(Person).filter(
            and_(
            Person.user == user,
            Person.pass_sha1 == pass_sha1
            )).first()

    def get_name(self, id):
        return self.db.session.query(Person).get(id).name

    def get_email(self, id):
        return self.db.session.query(Person).get(id).email


class PlateHandler():
    db = DB()

    def load(self, id):
        return self.db.session.query(Plate).get(id)
    

class GrowthRawHandler():
    db = DB()

    def load_by_exp_id(self, exp_id):
        return self.db.session.query(GrowthRaw).filter(
            GrowthRaw.exp_id == exp_id).all()
    
    def create(self, exp_id, col, row, con, ltg, mgr, spg):
        growth_raw = GrowthRaw(
            exp_id = exp_id,
            col = col,
            row = row,
            con = con,
            ltg = ltg,
            mgr = mgr,
            spg = spg
            )
        self.db.session.add(growth_raw)
        self.db.session.commit()
        return growth_raw
    
    def delete_by_exp_id(self, exp_id):
        self.db.session.query(GrowthRaw).filter(
            GrowthRaw.exp_id == exp_id).delete()
        self.db.session.commit()


class GrowthHandler():
    db = DB()

    def load_by_exp_id(self, exp_id):
        return self.db.session.query(Growth).filter(
            Growth.exp_id == exp_id).all()
    
    def create(self, exp_id, col, row, con, ltg, mgr, spg):
        growth = Growth(
            exp_id = exp_id,
            col = col,
            row = row,
            con = con,
            ltg = ltg,
            mgr = mgr,
            spg = spg
            )
        self.db.session.add(growth)
        self.db.session.commit()
        return growth
    
    def delete_by_exp_id(self, exp_id):
        self.db.session.query(Growth).filter(
            Growth.exp_id == exp_id).delete()
        self.db.session.commit()


class ColonyHandler():
    db = DB()

    def load_by_exp_id(self, exp_id):
        return self.db.session.query(Colony).filter(
            Colony.exp_id == exp_id).all()

    def create(self, exp_id, col, row, location, areas, masss, cmasss):
        colony = Colony(
            exp_id = exp_id,
            col = col,
            row = row,
            location = location,
            areas = areas,
            masss = masss,
            cmasss = cmasss
            )
        self.db.session.add(colony)
        self.db.session.commit()
        return colony
    
    def delete_by_exp_id(self, exp_id):
        self.db.session.query(Colony).filter(
            Colony.exp_id == exp_id).delete()
        self.db.session.commit()

    def get_by_exp_id(self, exp_id):
        return self.db.session.query(Colony).filter(
            Colony.exp_id == exp_id
            ).all()


if __name__ == "__main__":
    sh = ScannerHandler()
    #scanners = sh.get_scanners()
    #print scanners[0].exp_ids

    sih = ScanimgHandler()
    #scanimg = sih.create(1,'1|1|1|1')
    #print scanimg.id

    ih = ImgHandler()
    #img = ih.create(1,100)
    #print img.id

    eh = ExpHandler()
    #exp = eh.load(1)
    #print exp.project

    ph = PersonHandler()


