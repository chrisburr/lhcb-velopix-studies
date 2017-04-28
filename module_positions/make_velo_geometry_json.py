#!/usr/bin/env python
from __future__ import division
from __future__ import print_function

import argparse
import json
import os

import GaudiPython

XYZPoint = GaudiPython.gbl.ROOT.Math.XYZPoint


def scan_to_edge(geo, start_point, axis, direction):
    assert axis in ('X', 'Y', 'Z')
    assert direction in (-1, 1)
    p_local = XYZPoint(start_point)
    assert geo.isInside(geo.toGlobal(p_local))
    # Find the end of the ladder iteratively
    while abs(direction) > 1e-8:
        if geo.isInside(geo.toGlobal(p_local)):
            getattr(p_local, 'Set'+axis)(getattr(p_local, axis)()+direction)
        else:
            getattr(p_local, 'Set'+axis)(getattr(p_local, axis)()-direction)
            direction /= 10.
    # Step back a little so we don't get stuck due to numerical instability
    getattr(p_local, 'Set'+axis)(getattr(p_local, axis)()-direction)
    # We still be inside the ladder
    assert geo.isInside(geo.toGlobal(p_local))
    return p_local


def find_corners_of_cuboid(geo):
    corners = {}
    # Find the point A
    corners['A'] = scan_to_edge(geo, XYZPoint(1e-5, 1e-5, 1e-5), 'X', -1)
    corners['A'] = scan_to_edge(geo, corners['A'], 'Y', -1)
    corners['A'] = scan_to_edge(geo, corners['A'], 'Z', -1)
    # Find points B, D and E
    corners['B'] = scan_to_edge(geo, corners['A'], 'X', 1)
    corners['D'] = scan_to_edge(geo, corners['A'], 'Y', 1)
    corners['E'] = scan_to_edge(geo, corners['A'], 'Z', 1)
    # Find point C
    corners['C'] = scan_to_edge(geo, corners['B'], 'Y', 1)
    # Find points G
    corners['G'] = scan_to_edge(geo, corners['C'], 'Z', 1)
    # Find points F and H
    corners['F'] = scan_to_edge(geo, corners['G'], 'Y', -1)
    corners['H'] = scan_to_edge(geo, corners['G'], 'X', -1)

    return corners


def make_geometry_json(misaligned=False):
    if misaligned:
        options_fn = 'options_{}.py'.format(misaligned)
        output_fn_local = 'output/velo_geometry_{}_local.json'.format(misaligned)
        output_fn_global = 'output/velo_geometry_{}_global.json'.format(misaligned)
        sides = ['Left', 'Right']
    else:
        options_fn = 'options.py'
        output_fn_local = 'output/velo_geometry_local.json'
        output_fn_global = 'output/velo_geometry_global.json'
        sides = ['Right', 'Left']

    appMgr = GaudiPython.AppMgr(outputlevel=3, joboptions=options_fn)
    det = appMgr.detSvc()

    velo_geometry_local = {}
    velo_geometry_global = {}
    for i in range(52):
        module_key = (
            '/dd/Structure/LHCb/BeforeMagnetRegion/VP/VP{side}/'
            'Module{i:002d}WithSupport/Module{i:002d}'
            .format(i=i, side=sides[i % 2 == 1])
        )
        for ladder in det[module_key].childIDetectorElements():
            geo = ladder.geometry()
            corners = find_corners_of_cuboid(geo)

            # Convert the XYZPoint to tuples
            pos_local, pos_global = {}, {}
            for key, point_loc in corners.items():
                point_glob = geo.toGlobal(point_loc)
                pos_local[key] = (point_loc.x(), point_loc.y(), point_loc.z())
                pos_global[key] = (point_glob.x(), point_glob.y(), point_glob.z())

            velo_geometry_local[ladder.name()] = pos_local
            velo_geometry_global[ladder.name()] = pos_global

    # Dump the geometry to json
    with open(output_fn_local, 'wt') as f:
        json.dump(velo_geometry_local, f)

    with open(output_fn_global, 'wt') as f:
        json.dump(velo_geometry_global, f)

    return velo_geometry_local, velo_geometry_global


if __name__ == '__main__':
    if not os.path.isdir('output'):
        os.makedirs('output')
    parser = argparse.ArgumentParser()
    parser.add_argument('--misalignment', required=False, default='')
    make_geometry_json(misaligned=parser.parse_args().misalignment)
