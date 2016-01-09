#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""
Database operation modules

データベース操作
"""


from database import Database
from schema import Person, Batch


def find_person(user, passwd):
    table = "person"
    select = "id"
    where = "user='%s' AND passwd='%s'" % (user, passwd)
    db = Database()
    res = db.fetchone(table, select, where)
    if res == None:
        return None
    return Person(res[0])


def get_booked_batchs(person_id):
    table = "batch"
    select = "id"
    where = "status=('waiting the experiment' OR 'monitoring') AND person_id=%s" % person_id
    db = Database()
    res = db.fetchall(table, select, where)
    if res == None:
        return None
    return [Batch(i[0]) for i in res]


if __name__ == "__main__":
    pass
