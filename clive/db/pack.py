#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""
Mass data operation

大量データの処理

連続insertにより効率的にputする
"""

from database import Database, get_maxid


def mput_colonys(colonys):
    table = colonys[0].tablename
    sql = "INSERT INTO %s" % table
    sql += " (%s)" % ", ".join(colonys[0].items)
    sql += " VALUES "

    colony_id = get_maxid(table) + 1
    vals = []
    for colony in colonys:
        vals += ["(%d,%d,%d,%d,'%s','%s','%s','%s')" % (
                colony_id,
                colony.exp_id,
                colony.col,
                colony.row,
                colony.location,
                colony.areas,
                colony.masss,
                colony.cmasss
                ) ]
        colony_id += 1
    sqls = []
    capa = 100   # capacity
    n = len(vals)
    n_pack = n/capa
    for i in range(n_pack):
        sqls += [sql + ", ".join(vals[capa*i:capa*(i+1)])]
    sqls += [sql + ", ".join(vals[capa*n_pack:n])]
    db = Database()
    db.execute_sqls(table, sqls)
    

def mput_growths(growths):
    table = growths[0].tablename
    sql = "INSERT INTO %s" % table
    sql += " (%s)" % ", ".join(growths[0].items)
    sql += " VALUES "
    
    growth_id = get_maxid(table) + 1
    vals = []
    for growth in growths:
        vals += ["(%d,%d,%d,%d,%s,%f,%f,%f)" % (
                growth_id,
                growth.exp_id,
                growth.col,
                growth.row,
                growth.con,
                growth.ltg,
                growth.mgr,
                growth.spg
                ) ]
        growth_id += 1
    sqls = []
    capa = 100
    n = len(vals)
    n_pack = n/capa
    for i in range(n_pack):
        sqls += [sql + ", ".join(vals[capa*i:capa*(i+1)])]
    sqls += [sql + ", ".join(vals[capa*n_pack:n])]
    db = Database()
    db.execute_sqls(table, sqls)

