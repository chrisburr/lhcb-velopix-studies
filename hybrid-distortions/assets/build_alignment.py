#!/usr/bin/env python3
# [SublimeLinter flake8-max-line-length:120]
from __future__ import division
from __future__ import print_function

import argparse
from random import gauss
from math import asin, cos, sin
from os import makedirs
from os.path import dirname, isdir, join


HEADER = (
    '<?xml version="1.0" encoding="ISO-8859-1"?>\n'
    '<!DOCTYPE DDDB SYSTEM "../../../DTD/structure.dtd">\n'
    '<DDDB>\n'
    '\n'
)

MODULE = (
    '  <condition classID="{class_id}"  name="{name}">\n'
    '    <paramVector  name="dPosXYZ"  type="double"> {tx} {ty} {tz} </paramVector>\n'
    '    <paramVector  name="dRotXYZ"  type="double"> {rx} {ry} {rz} </paramVector>\n'
    '  </condition>\n'
    '  \n'
)

FOOTER = (
    '</DDDB>\n'
)


def make_global_xml(basedir):
    global_fn = join(basedir, 'SIMCOND/Conditions/VP/Alignment/Global.xml')
    if not isdir(dirname(global_fn)):
        makedirs(dirname(global_fn))

    xml = HEADER
    xml += MODULE.format(
        class_id=6, name='VPSystem',
        tx=0, ty=0, tz=0,
        rx=0, ry=0, rz=0
    )
    xml += MODULE.format(
        class_id=1008106, name='VPLeft',
        tx=0, ty=0, tz=0,
        rx=0, ry=0, rz=0
    )
    xml += MODULE.format(
        class_id=1008106, name='VPRight',
        tx=0, ty=0, tz=0,
        rx=0, ry=0, rz=0
    )
    xml += FOOTER
    with open(global_fn, 'wt') as f:
        f.write(xml)


def make_modules_xml(basedir, x_distortion, y_distortion, sigma, alternate=False):
    modules_fn = join(basedir, 'SIMCOND/Conditions/VP/Alignment/Modules.xml')
    if not isdir(dirname(basedir)):
        makedirs(dirname(basedir))

    xml = HEADER
    module_width = 100000
    for i in range(52):
        if alternate and int(i/2) % 2 == 0:
            xml += MODULE.format(
                class_id=6, name='Module{i:02d}'.format(i=i),
                tx=0, ty=0, tz=0,
                rx=0, ry=0, rz=0
            )
            continue

        rx = asin(x_distortion / module_width)
        if sigma > 0:
            rx = gauss(rx, sigma*abs(rx))

        ry = asin(y_distortion / module_width)
        if sigma > 0:
            ry = gauss(ry, sigma*abs(ry))

        rz = 0

        assert rx == rz == 0
        x_over_reach = 22810
        tx = - module_width/1000 * (1-cos(ry)) * (1-x_over_reach/module_width)
        tz = - module_width/1000 * sin(ry) * (1-x_over_reach/module_width)

        xml += MODULE.format(
            class_id=6, name='Module{i:02d}'.format(i=i),
            tx=tx, ty=0, tz=tz,
            rx=rx, ry=ry, rz=rz
        )
    xml += FOOTER
    with open(modules_fn, 'wt') as f:
        f.write(xml)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make the global and modules xml')
    parser.add_argument('--basedir')
    parser.add_argument('--x-distortion', type=float, default=0)
    parser.add_argument('--y-distortion', type=float, default=0)
    parser.add_argument('--sigma', type=float, default=0)
    parser.add_argument('--alternate', action='store_true')

    args = parser.parse_args()

    make_global_xml(args.basedir)
    make_modules_xml(args.basedir, args.x_distortion, args.y_distortion, args.sigma, args.alternate)
