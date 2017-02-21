#!/usr/bin/env python3
# [SublimeLinter flake8-max-line-length:120]
import argparse

from os import makedirs
from os.path import dirname, isdir


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


def make_global_xml(filename):
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
    with open(filename, 'wt') as f:
        f.write(xml)


def make_modules_xml(filename):
    xml = HEADER
    for i in range(52):
        xml += MODULE.format(
            class_id=6, name='Module{i:02d}'.format(i=i),
            tx=0, ty=0, tz=0,
            rx=0, ry=0, rz=0
        )
    xml += FOOTER
    with open(filename, 'wt') as f:
        f.write(xml)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make the global and modules xml')
    parser.add_argument('--global-fn')
    parser.add_argument('--modules-fn')

    args = parser.parse_args()

    if not isdir(dirname(args.global_fn)):
        makedirs(dirname(args.global_fn))
    make_global_xml(args.global_fn)

    if not isdir(dirname(args.modules_fn)):
        makedirs(dirname(args.modules_fn))
    make_modules_xml(args.modules_fn)
