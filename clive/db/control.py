#!/usr/bin/env python2
# -*- coding:utf-8 -*-


"""
[NAME]
Scannerクラスの定義

[DESCRIPTION]
Scannerクラスの定義

"""

import datetime
from schema import Scanner, Person, Exp


def start_batch(batch):
    dt_start = datetime.datetime.now()
    dt_measure = datetime.timedelta(hours=batch.h_scan)
    dt_finish = dt_start + dt_measure

    person = Person(batch.person_id)
   
    sid2exp_ids = {}
    for pos2exp_id in batch.pos2exp_id.split("|"):
        pos, exp_id = pos2exp_id.split(":")
        sid, sind = map(int, pos.split("-"))
        if sid not in sid2exp_ids.keys():
            sid2exp_ids[sid] = []
        sid2exp_ids[sid] += [exp_id]
        exp = Exp(int(exp_id))
        exp.dt_start = dt_start
        exp.update()

    for sid, exp_ids in sid2exp_ids.items():
        exp_ids_str = "|".join(exp_ids)
        #for item in batch.poss_assig.split(","):
        #scanner_id, exp_ids = item.split("-")
        #scanner = Scanner(scanner_id)
        scanner = Scanner(sid)
        scanner.batch_id = batch.id
        scanner.person_name = person.name
        scanner.dt_start = dt_start
        scanner.dt_finish = dt_finish
        scanner.exp_ids = exp_ids_str
        scanner.update()

    batch.dt_start = dt_start
    batch.status = "monitoring"
    batch.update()


def cancel_batch(batch):
    sids = list(set([int(i.split(":")[0].split("-")[0])
                for i in batch.pos2exp_id.split("|")]))
    for sid in sids:
        scanner = Scanner(sid)
        scanner.clean()
    batch.status = "waiting the experiment"
    batch.update()


def abort_batch(batch):
    sids = list(set([int(i.split(":")[0].split("-")[0])
                for i in batch.pos2exp_id.split("|")]))
    for sid in sids:
        scanner = Scanner(sid)
        scanner.dt_finish = datetime.datetime.now() # 終了時刻を押した時刻にする
        scanner.update()
    batch.status = "Done"
    batch.update()
    

if __name__ == "__main__":
    pass
