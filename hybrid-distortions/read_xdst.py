# [SublimeLinter flake8-max-line-length:150]
from __future__ import division
from __future__ import print_function

from os.path import join
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

job_name = 'tip_x=0um_y=-1000um_sigma=0.2'
files = ['/pc2014-data3/cburr/hybrid_xdsts/155481706/Brunel.xdst']


def add_data():
    IOHelper('ROOT').inputFiles(files)

    CondDB().Upgrade = True
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


add_data()
configure()
appMgr, evt = track_tools.initialise()

output = {'tracks': [], 'clusters': []}
while True:
    n_event = track_tools.run()
    if not evt['/Event/Rec/Header'] or n_event > 10:
        break

    for n_t, track in enumerate(map(Track, evt['Rec/Track/Best'])):
        # Store the track information
        output['tracks'].append((
            n_event, n_t, track.track_type, track.rx, track.ry,
            track.px, track.py, track.pz
        ))
        print(*output['tracks'][-1])

        # Store the cluster information
        for n_c, hit in enumerate(track.vp_hits):
            residual, intercept = hit.fit()
            output['clusters'].append((
                n_event, n_t, n_c,
                hit.cluster.x, hit.cluster.y, hit.cluster.z,
                intercept.x(), intercept.y(), intercept.z(),
                residual.x(), residual.y(), residual.z(),
            ))
            print(' > ', *output['clusters'][-1])

with open(job_name+'.json', 'wt') as f:
    json.dump(output, f)
