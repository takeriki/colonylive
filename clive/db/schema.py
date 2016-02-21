#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""
Database schema (Table構成)の定義

"""

from database import Table

class Exp(Table):
    tablename = "exp" 
    items = ["id",
             "batch_id",
             "project",
             "plate_id",
             "person_id",
             "medium",
             "conditions",
             "h_scan",
             "dt_start",
             "pos_scan",
             "mins_grow",
             "step_done",
             "n_death",
             "pcc",
             "failure",
             "note",
             "in_process"]


class Person(Table):
    tablename = "person"
    items = ["id",
             "user",
             "passwd",
             "name",
             "email"]
    

class Batch(Table):
    tablename = "batch" 
    items = ["id",
             "project",
             "person_id",
             "num_plates",
             "pos2exp_id",
             "dt_start",
             "h_scan",
             "status"]

            
class Imgscan(Table):
    tablename = "img_scan" 
    items = ["id",
             "dt_scan",
             "scanner_id",
             "exp_ids",
             "min_grow"]


class Scanner(Table):
    tablename = "scanner"
    items = ["id",
             "person_name",
             "dt_start",
             "dt_finish",
             "exp_ids",
             "min_grows"]


class Colony(Table):
    tablename = "colony"
    items = ["id",
             "exp_id",
             "col",
             "row",
             "location",
             "areas",
             "masss",
             "cmasss"]


class Growth(Table):
    tablename = "growth"
    items = ["id",
             "exp_id",
             "col",
             "row",
             "con",
             "ltg",
             "mgr",
             "spg"]


class Ngrowth(Table):
    tablename = "ngrowth"
    items = ["id",
             "exp_id",
             "col",
             "row",
             "con",
             "ltg",
             "mgr",
             "spg"]


if __name__ == "__main__":
    pass
