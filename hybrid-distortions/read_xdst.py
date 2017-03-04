# [SublimeLinter flake8-max-line-length:150]
from __future__ import division
from __future__ import print_function

from os.path import join
import os

from LHCbConfig import ApplicationMgr, lhcbApp
from GaudiConf import IOHelper
from Configurables import CondDB
from Configurables import CondDBAccessSvc
from Configurables import GaudiSequencer
from Configurables import PrPixelStoreClusters
import GaudiPython

import track_tools
from track_tools import Track


def add_data():
    job_name = 'tip_x=0um_y=-1000um_sigma=0.2'
    files = ['/pc2014-data3/cburr/hybrid_xdsts/155481706/Brunel.xdst']

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
appMgr = GaudiPython.AppMgr()
evt = appMgr.evtsvc()
track_tools.initialise(appMgr, evt)

while True:
    appMgr.run(1)

    if not evt['/Event/Rec/Header']:
        break

    for track in map(Track, evt['Rec/Track/Best']):
        print(track.track_type, track.rx, track.ry)
    break
