#!/usr/bin/python


class GrowthPack():
    def __init__(self, poss):
        poss = sorted(poss, key=lambda x:(x[1],x[0]))
        self.poss = poss
        self.pos2data = {}
        for pos in poss:
            self.pos2data[pos] = []

    def add(self, pos, con, ltg, mgr, spg):
        data = [con, ltg, mgr, spg]
        self.pos2data[pos] = data

