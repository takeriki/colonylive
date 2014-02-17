"""
Database management with SqlAlchemy

"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from clive.core.conf import Configure
cfg = Configure()
host = cfg[('db','host')]
db = cfg[('db','db')]
user = cfg[('db','user')]
passwd = cfg[('db','pass')]
port = cfg[('db','port')]


class DB:
    def __init__(self):
        self.engine = create_engine(
            "mysql://%s:%s@%s:%s/%s" % 
            (user, passwd, host, port, db),
            pool_recycle=3600)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def reconnect(self):
        self.session.close()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

if __name__ == "__main__":
    db = DB()
    print db
