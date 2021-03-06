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
from tqdm import tqdm

from Configurables import CondDB
from Configurables import CondDBAccessSvc
from Configurables import GaudiSequencer
from Configurables import NoPIDsParticleMaker
from Configurables import PrPixelStoreClusters
from GaudiConf import IOHelper
from LHCbConfig import ApplicationMgr, lhcbApp
from LHCbMath import XYZPoint

import track_tools
from track_tools import Track


def add_data(job_name, job_id):
    IOHelper('ROOT').inputFiles(glob(join('output/scenarios', job_name, 'hists', str(job_id), 'Brunel.xdst')))

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

    PreLoadPions = NoPIDsParticleMaker('PreLoadPions')
    PreLoadPions.Particle = 'pions'
    PreLoadKaons = NoPIDsParticleMaker('PreLoadKaons')
    PreLoadKaons.Particle = 'kaon'
    appConf.TopAlg += [PreLoadPions, PreLoadKaons]


def read_tracks_and_clusters(scenario, job_id, n_events):
    add_data(scenario, job_id)
    configure()
    appMgr, evt = track_tools.initialise()

    true_clusters_fn = 'output/scenarios/Original_DB/clusters_'+str(job_id)+'.msg'
    if isfile(true_clusters_fn) and scenario != 'Original_DB':
        true_clusters = pd.read_msgpack(true_clusters_fn)
        if isinstance(true_clusters, list):
            true_clusters = pd.concat(true_clusters)
            true_clusters['run_number'] = pd.to_numeric(true_clusters['run_number'], downcast='unsigned')
            true_clusters['event_number'] = pd.to_numeric(true_clusters['event_number'], downcast='unsigned')
            true_clusters.set_index(['run_number', 'event_number', 'channel_id'], inplace=True)
            true_clusters.sortlevel(inplace=True)
    else:
        true_clusters = None

    clusters = []
    tracks = []
    residuals = []
    particles = []

    write_msgpack.do_append = False

    # pbar = tqdm(total=100)
    while True:
        # pbar.update(1)
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

        # Make a dataframe of just this event's clusters (for speed)
        if true_clusters is None:
            true_clusters_for_event = None
        else:
            # true_clusters_for_event = true_clusters.query(
            #     '(run_number == {run_number}) & (event_number == {event_number})'
            #     .format(run_number=run_number, event_number=event_number)
            # )
            true_clusters_for_event = true_clusters.loc[run_number, event_number]

        # Store information about the tracks
        for track_number, track in enumerate(map(Track, evt['Rec/Track/Best'])):
            try:
                mc_particle = track.mc_particle
            except ValueError:
                mc_particle_px, mc_particle_py, mc_particle_pz = None, None, None
            else:
                mc_particle_px = mc_particle.px
                mc_particle_py = mc_particle.py
                mc_particle_pz = mc_particle.pz

            IP3D, IPx, IPy = track.ip

            tracks.append([
                run_number, event_number, track_number, track.key, track.track_type,
                track.rx, track.ry, track.px, track.py, track.pz,
                mc_particle_px, mc_particle_py, mc_particle_pz,
                IP3D, IPx, IPy
            ])

            # Insert a fake UT cluster
            fake_ut_channel_id = -1 * (int(run_number*1e10) + int(event_number*1e3) + int(track_number))
            fake_position = track.fit_to_point(XYZPoint(0, 0, 2500), minimise=False)
            clusters.append([run_number, event_number, fake_ut_channel_id, fake_position.x(), fake_position.y(), fake_position.z()])

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
                if true_clusters_for_event is None:
                    hit_data.extend([None]*6)
                else:
                    # true_cluster = true_clusters_for_event[
                    #     (true_clusters_for_event.channel_id == hit.cluster.channel_id)
                    # ]
                    # true_cluster = true_clusters_for_event.loc[hit.cluster.channel_id]
                    # assert len(true_cluster) == 1
                    # true_cluster = true_cluster.iloc[0]
                    true_point = XYZPoint(
                        true_clusters_for_event.at[float(hit.cluster.channel_id), 'x'],
                        true_clusters_for_event.at[float(hit.cluster.channel_id), 'y'],
                        true_clusters_for_event.at[float(hit.cluster.channel_id), 'z']
                    )
                    true_intercept, true_residual = track.fit_to_point(true_point)
                    hit_data.extend([true_intercept.x(), true_intercept.y(), true_intercept.z()])
                    hit_data.extend([true_residual.x(), true_residual.y(), true_residual.z()])

                residuals.append(hit_data)

        # Add infromation about any truth matched particles we can find:
        for kp_track, km_track, pi_track in track_tools.get_dstars():
            try:
                D0, pv, pv_ipchi2, d0_vertex, true_d0_vertex, true_dst_vertex, true, fitted, kp, km, pi = track_tools.fit_vertex(kp_track, km_track, pi_track)
            except ValueError:
                pass
            else:
                D0_mc = kp_track.mc_particle.mother
                kp_mc = kp_track.mc_particle
                km_mc = km_track.mc_particle
                pi_mc = pi_track.mc_particle
                particles.append([
                    run_number, event_number, kp_track.key, km_track.key, pi_track.key, d0_vertex.chi2(), d0_vertex.chi2PerDoF(),
                    D0.momentum().x(), D0.momentum().y(), D0.momentum().z(), D0_mc.px, D0_mc.py, D0_mc.pz,
                    d0_vertex.position().x(), d0_vertex.position().y(), d0_vertex.position().z(),
                    true_d0_vertex.x(), true_d0_vertex.y(), true_d0_vertex.z(),
                    pv.position().x(), pv.position().y(), pv.position().z(), pv_ipchi2,
                    true_dst_vertex.x(), true_dst_vertex.y(), true_dst_vertex.z(),
                    kp_track.px, kp_track.py, kp_track.pz, kp_mc.px, kp_mc.py, kp_mc.pz,
                    km_track.px, km_track.py, km_track.pz, km_mc.px, km_mc.py, km_mc.pz,
                    pi_track.px, pi_track.py, pi_track.pz, pi_mc.px, pi_mc.py, pi_mc.pz,
                ])

        # Store output every 10 events
        if n_event % 10:
            write_msgpack(scenario, job_id, clusters, tracks, particles, residuals)
            # Clear the existing arrays
            clusters = []
            tracks = []
            residuals = []
            particles = []

    # pbar.close()

    write_msgpack(scenario, job_id, clusters, tracks, particles, residuals)


def write_msgpack(scenario, job_id, clusters, tracks, particles, residuals):
    out_dir = join('output/scenarios', scenario)

    clusters = pd.DataFrame(clusters, columns=['run_number', 'event_number', 'channel_id', 'x', 'y', 'z'])
    clusters.to_msgpack(join(out_dir, 'clusters_'+str(job_id)+'.msg'), append=write_msgpack.do_append)

    tracks = pd.DataFrame(tracks, columns=[
        'run_number', 'event_number', 'track_number', 'track_key', 'track_type',
        'tx', 'ty', 'px', 'py', 'pz', 'true_px', 'true_py', 'true_pz', 'IP3D', 'IPx', 'IPy'
    ])
    tracks.to_msgpack(join(out_dir, 'tracks_'+str(job_id)+'.msg'), append=write_msgpack.do_append)

    # TODO Prompt and charge information
    particles = pd.DataFrame(particles, columns=[
        'run_number', 'event_number', 'kp_track_key', 'km_track_key', 'pi_track_key', 'vertex_chi2', 'vertex_chi2_per_DoF',
        'D0_p_x', 'D0_p_y', 'D0_p_z', 'D0_true_p_x', 'D0_true_p_y', 'D0_true_p_z', 'vertex_x', 'vertex_y', 'vertex_z',
        'true_d0_vertex_x', 'true_d0_vertex_y', 'true_d0_vertex_z',
        'pv_x', 'pv_y', 'pv_z', 'pv_ipchi2',
        'true_dst_vertex_x', 'true_dst_vertex_y', 'true_dst_vertex_z',
        'kp_px', 'kp_py', 'kp_pz', 'kp_true_px', 'kp_true_py', 'kp_true_pz',
        'km_px', 'km_py', 'km_pz', 'km_true_px', 'km_true_py', 'km_true_pz',
        'pi_px', 'pi_py', 'pi_pz', 'pi_true_px', 'pi_true_py', 'pi_true_pz',
    ])
    particles.to_msgpack(join(out_dir, 'particles_'+str(job_id)+'.msg'), append=write_msgpack.do_append)

    residuals = pd.DataFrame(residuals, columns=[
        'run_number', 'event_number', 'track_number', 'cluster_channel_id',
        'module', 'sensor', 'chip', 'row', 'col', 'scol',
        'intercept_x', 'intercept_y', 'intercept_z', 'residual_x', 'residual_y', 'residual_z',
        'true_intercept_x', 'true_intercept_y', 'true_intercept_z', 'true_residual_x', 'true_residual_y', 'true_residual_z',
    ])
    residuals.to_msgpack(join(out_dir, 'residuals_'+str(job_id)+'.msg'), append=write_msgpack.do_append)

    # Append after the first write
    write_msgpack.do_append = True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Produce JSON with reconstruction information')
    parser.add_argument(
        'scenario',
        choices=map(basename, glob('output/scenarios/*')),
        help='The reconstruction scenario to use'
    )
    parser.add_argument(
        '--job-id', type=int, required=True,
        help='The reconstruction scenario to use'
    )

    parser.add_argument(
        '--n-events', '-n', type=int, default=100,
        help='The reconstruction scenario to use'
    )

    args = parser.parse_args()
    read_tracks_and_clusters(args.scenario, args.job_id, args.n_events)
