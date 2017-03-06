# [SublimeLinter flake8-max-line-length:150]
from __future__ import division
from __future__ import print_function

import argparse
from glob import glob
from os.path import join, basename, isfile
import os
import sys

# Lets get an acceptable version of pandas
# Create using 'pip install --target my_pandas pandas'
sys.path.insert(0, os.path.abspath('./my_pandas/'))  # NOQA
import pandas as pd

from Configurables import CondDB
from Configurables import CondDBAccessSvc
from Configurables import GaudiSequencer
from Configurables import PrPixelStoreClusters
from GaudiConf import IOHelper
from LHCbConfig import ApplicationMgr, lhcbApp
from LHCbMath import XYZPoint

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

    true_clusters_fn = 'output/scenarios/Original_DB/clusters.msg'
    if isfile(true_clusters_fn):
        true_clusters = pd.read_msgpack(true_clusters_fn)
    else:
        true_clusters = None

    clusters = []
    tracks = []
    residuals = []

    while True:
        n_event = track_tools.run()

        # Look at the header
        header = evt['/Event/Rec/Header']
        if not header or n_event >= n_events:
            break
        run_number = header.runNumber()
        event_number = header.evtNumber()

        # Store information about the clusters
        for channel_id, cluster in track_tools.get_clusters().items():
            clusters.append([run_number, event_number, channel_id, cluster.x, cluster.y, cluster.z])

        # Store information about the tracks
        for track_number, track in enumerate(map(Track, evt['Rec/Track/Best'])):
            tracks.append([
                run_number, event_number, track_number, track.track_type,
                track.rx, track.ry, track.px, track.py, track.pz
            ])

            # Store information about the associated clusters
            for hit in track.vp_hits:
                hit_data = [
                    run_number, event_number, track_number, hit.cluster.channel_id,
                    hit.module, hit.sensor, hit.chip, hit.row, hit.col, hit.scol
                ]

                # Calculate the residual for this geometry
                intercept, residual = track.fit_to_point(hit.cluster.position)
                hit_data.extend([intercept.x(), intercept.y(), intercept.z()])
                hit_data.extend([residual.x(), residual.y(), residual.z()])

                # Calculate the residual for the true geometry
                if true_clusters is None:
                    hit_data.extend([None]*6)
                else:
                    true_cluster = true_clusters[
                        (true_clusters.run_number == run_number) &
                        (true_clusters.event_number == event_number) &
                        (true_clusters.channel_id == hit.cluster.channel_id)
                    ]
                    assert len(true_cluster) == 1
                    true_cluster = true_cluster.iloc[0]
                    true_point = XYZPoint(true_cluster.x, true_cluster.y, true_cluster.z)
                    true_intercept, true_residual = track.fit_to_point(true_point)
                    hit_data.extend([true_intercept.x(), true_intercept.y(), true_intercept.z()])
                    hit_data.extend([true_residual.x(), true_residual.y(), true_residual.z()])

                residuals.append(hit_data)

    out_dir = join('output/scenarios', scenario)

    clusters = pd.DataFrame(clusters, columns=['run_number', 'event_number', 'channel_id', 'x', 'y', 'z'])
    clusters.to_msgpack(join(out_dir, 'clusters.msg'))

    tracks = pd.DataFrame(tracks, columns=['run_number', 'event_number', 'track_number', 'track_type', 'tx', 'ty', 'px', 'py', 'pz'])
    tracks.to_msgpack(join(out_dir, 'tracks.msg'))

    residuals = pd.DataFrame(residuals, columns=[
        'run_number', 'event_number', 'track_number', 'cluster_channel_id',
        'module', 'sensor', 'chip', 'row', 'col', 'scol',
        'intercept_x', 'intercept_y', 'intercept_z', 'residual_x', 'residual_y', 'residual_z',
        'true_intercept_x', 'true_intercept_y', 'true_intercept_z', 'true_residual_x', 'true_residual_y', 'true_residual_z',
    ])
    residuals.to_msgpack(join(out_dir, 'residuals.msg'))


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
