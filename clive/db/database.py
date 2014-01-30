"""
Database management with SqlAlchemy

"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from clive.core.conf import Configure
cfg = Configure()
tmp = cfg[('db','main')].split(',')
DB_PARS = [i.replace(' ','') for i in tmp]


class DB:

    def __init__(self):
        (host, db, port, user, passwd) = DB_PARS
        engine = create_engine("mysql://%s:%s@%s:%s/%s" % 
            (user, passwd, host, port, db), pool_recycle=3600)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def fetch(self, sql):
        cur = self.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        cur.close()
        return res

    def change(self, sql):
        cur = self.cursor()
        try:
            cur.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
        cur.close()


if __name__ == "__main__":
    db = DB()
    print db
