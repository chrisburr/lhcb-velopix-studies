#!/usr/bin/env python
from __future__ import print_function

import argparse
import shutil
import os
from os.path import dirname, join

import GaudiPython


def get_ladders(i, det):
    module_key = (
        '/dd/Structure/LHCb/BeforeMagnetRegion/VP/VP{side}/'
        'Module{i:002d}WithSupport/Module{i:002d}'
        .format(i=i, side=['Left', 'Right'][i % 2 == 1])
    )
    for ladder in det[module_key].childIDetectorElements():
        point = GaudiPython.gbl.ROOT.Math.XYZPoint(0, 0, 0)
        point = ladder.geometry().toGlobal(point)
        yield ladder.name(), point.x(), point.y(), point.z()
        point = GaudiPython.gbl.ROOT.Math.XYZPoint(42.46, 14.08, 0)
        point = ladder.geometry().toGlobal(point)
        yield ladder.name(), point.x(), point.y(), point.z()


def format(f):
    return '{0:.12f}'.format(f).rjust(18)


def store_module_positions(options, output_fn):
    appMgr = GaudiPython.AppMgr(outputlevel=3, joboptions=options)

    det = appMgr.detSvc()

    with open(output_fn, 'wt') as f:
        for i in range(52):
            for name, x, y, z in get_ladders(i, det):
                f.write(name.rjust(85))
                f.write(format(x))
                f.write(format(y))
                f.write(format(z))
                f.write('\n')
                print(name, x, y, z)

    appMgr.exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--alignment-db', required=True)
    db = parser.parse_args().alignment_db

    output_fn = join(dirname(db), 'positions.txt')

    shutil.copy('output/DDDB.db', 'check_positions/DDDB.db')
    shutil.copy('output/SIMCOND.db', 'check_positions/SIMCOND.db')
    shutil.copy(db, 'check_positions/Alignment_SIMCOND.db')

    try:
        store_module_positions('check_positions/options.py', output_fn)
    finally:
        os.remove('check_positions/DDDB.db')
        os.remove('check_positions/SIMCOND.db')
        os.remove('check_positions/Alignment_SIMCOND.db')
        os.remove('Brunel-histos.root')
        os.remove('Brunel.xdst')
