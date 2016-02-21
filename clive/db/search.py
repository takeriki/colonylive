#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""
Database operation modules

データベース操作
"""


from database import Database
from schema import Person, Batch, Colony, Growth


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


def get_colonys_by_exp_id(exp_id):
    items = Colony.items
    select = ','.join(Colony.items)
    where = "exp_id='%d'" % (exp_id)
    db = Database()
    res = db.fetchall(Colony.tablename, select, where)
    if res == None:
        return None
    colonys = []
    for values in res:
        colony = Colony()
        for i, v in enumerate(values):
            colony.__dict__[items[i]] = v
        colonys += [colony]
    return colonys


def get_growths_by_exp_id(exp_id):
    items = Growth.items
    select = ','.join(Growth.items)
    where = "exp_id='%d'" % (exp_id)
    db = Database()
    res = db.fetchall(Growth.tablename, select, where)
    if res == None:
        return None
    growths = []
    for values in res:
        growth = Growth()
        for i, v in enumerate(values):
            growth.__dict__[items[i]] = v
        growths += [growth]
    return growths


if __name__ == "__main__":
    pass
