# [SublimeLinter flake8-max-line-length:150]
from __future__ import division
from __future__ import print_function

import argparse
from glob import glob
from os.path import join, basename
import os
import json

from LHCbConfig import ApplicationMgr, lhcbApp
from GaudiConf import IOHelper
from Configurables import CondDB
from Configurables import CondDBAccessSvc
from Configurables import GaudiSequencer
from Configurables import PrPixelStoreClusters

import track_tools
from track_tools import Track


def add_data(job_name):
    IOHelper('ROOT').inputFiles(glob(join('output/scenarios', job_name, 'xdsts/*.xdst')))

    CondDB().Upgrade = True
    if job_name == 'Original_DB':
        lhcbApp.DDDBtag = "dddb-20160304"
        lhcbApp.CondDBtag = "sim-20150716-vc-md100"
    else:
        CondDB().addLayer(dbFile=join(os.getcwd(), 'output/DDDB.db'), dbName="DDDB")
        CondDB().addLayer(dbFile=join(os.getcwd(), 'output/SIMCOND.db'), dbName="SIMCOND")
        alignment_conditions = CondDBAccessSvc("AlignmentConditions")
        alignment_conditions.ConnectionString = "sqlite_file:{}/output/scenarios/{}/Alignment_SIMCOND.db/SIMCOND".format(os.getcwd(), job_name)
        CondDB().addLayer(alignment_conditions)


def configure():
    lhcbApp.DataType = 'Upgrade'
    lhcbApp.Simulation = True
    lhcbApp.setProp(
        "Detectors",
        ['VP', 'UT', 'FT', 'Rich1Pmt', 'Rich2Pmt', 'Spd', 'Prs', 'Ecal', 'Hcal', 'Muon', 'Magnet']
    )

    vp_sequence = GaudiSequencer('PrPixelStoreClusters_Seq')
    vp_sequence.Members.append(PrPixelStoreClusters())

    appConf = ApplicationMgr()
    appConf.ExtSvc += ['ToolSvc', 'DataOnDemandSvc']
    appConf.TopAlg += [vp_sequence]


def read_tracks_and_clusters(scenario, n_events):
    add_data(scenario)
    configure()
    appMgr, evt = track_tools.initialise()

    output = {'tracks': [], 'clusters': []}
    while True:
        n_event = track_tools.run()
        if not evt['/Event/Rec/Header'] or n_event > n_events:
            break

        for n_t, track in enumerate(map(Track, evt['Rec/Track/Best'])):
            # Store the track information
            output['tracks'].append((
                n_event, n_t, track.track_type, track.rx, track.ry,
                track.px, track.py, track.pz
            ))
            # print(*output['tracks'][-1])

            # Store the cluster information
            for n_c, hit in enumerate(track.vp_hits):
                residual, intercept = hit.fit()
                output['clusters'].append((
                    n_event, n_t, n_c,
                    hit.sidepos, hit.module, hit.sensor, hit.station, hit.chip,
                    hit.row, hit.col, hit.scol,
                    hit.cluster.x, hit.cluster.y, hit.cluster.z,
                    intercept.x(), intercept.y(), intercept.z(),
                    residual.x(), residual.y(), residual.z(),
                ))
                # print(' > ', *output['clusters'][-1])

    fn = join('output/scenarios', scenario, 'tracks_and_clusters.json')
    print('Writing json to', fn)
    with open(fn, 'wt') as f:
        json.dump(output, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Produce JSON with reconstruction information')
    parser.add_argument(
        'scenario',
        choices=map(basename, glob('output/scenarios/*')),
        help='The reconstruction scenario to use'
    )
    parser.add_argument(
        '--n-events', '-n', type=int, default=100,
        help='The reconstruction scenario to use'
    )

    args = parser.parse_args()
    read_tracks_and_clusters(args.scenario, args.n_events)
