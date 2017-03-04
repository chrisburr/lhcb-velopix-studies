# [SublimeLinter flake8-max-line-length:150]
from __future__ import division
from __future__ import print_function

from math import sqrt
from os.path import join
import os
from collections import defaultdict
import json
from glob import glob

import pandas as pd
import scipy.optimize
import ROOT
import LHCbMath

from ROOT import (
    TFile, TCanvas, TH1F, TH2F, gROOT, TF1, gStyle, TText, Double, TLatex
)
import Panoramix
from LHCbConfig import ApplicationMgr, INFO, EventSelector, lhcbApp, addDBTags
from TrackFitter.ConfiguredFitters import ConfiguredMasterFitter
from GaudiConf import IOHelper
from LinkerInstances.eventassoc import linkedTo
from Configurables import CondDB
from Configurables import CondDBAccessSvc
from Configurables import GaudiSequencer
from Configurables import PrPixelStoreClusters
import GaudiPython
from Configurables import LHCbApp
from LinkerInstances.eventassoc import linkedTo
from Configurables import MeasurementProvider


job_name = 'tip_x=0um_y=-1000um_sigma=0.2'
files = ['/pc2014-data3/cburr/hybrid_xdsts/155481706/Brunel.xdst']


LineTraj = GaudiPython.gbl.LHCb.LineTraj
MCParticle = GaudiPython.gbl.LHCb.MCParticle
Track = GaudiPython.gbl.LHCb.Track
Range = GaudiPython.gbl.std.pair('double', 'double')
XYZPoint = LHCbMath.XYZPoint
XYZVector = LHCbMath.XYZVector

lhcbApp.DataType = 'Upgrade'
lhcbApp.Simulation = True
lhcbApp.setProp(
    "Detectors",
    ['VP', 'UT', 'FT', 'Rich1Pmt', 'Rich2Pmt', 'Spd', 'Prs', 'Ecal', 'Hcal', 'Muon', 'Magnet']
)

IOHelper('ROOT').inputFiles(files)

CondDB().Upgrade = True
CondDB().addLayer(dbFile=join(os.getcwd(), 'output/DDDB.db'), dbName="DDDB")
CondDB().addLayer(dbFile=join(os.getcwd(), 'output/SIMCOND.db'), dbName="SIMCOND")
alignment_conditions = CondDBAccessSvc("AlignmentConditions")
alignment_conditions.ConnectionString = "sqlite_file:{}/output/scenarios/{}/Alignment_SIMCOND.db/SIMCOND".format(os.getcwd(), job_name)
CondDB().addLayer(alignment_conditions)

fitter = ConfiguredMasterFitter("TrackMasterFitter")
fitter.addTool(MeasurementProvider(), name='MeasProvider')
# # TODO Why isn't this done in ConfiguredFitters.py?
fitter.MeasProvider.IgnoreVelo = True
fitter.MeasProvider.IgnoreTT = True
fitter.MeasProvider.IgnoreIT = True
fitter.MeasProvider.IgnoreOT = True
fitter.MeasProvider.IgnoreVP = False
fitter.MeasProvider.IgnoreFT = False
fitter.MeasProvider.IgnoreUT = True


# decodingSeq = GaudiSequencer("RecoDecodingSeq")
# from DAQSys.Decoders import DecoderDB
# from DAQSys.DecoderClass import decodersForBank
# from Configurables import STOfflinePosition
# decs = [
#     decodersForBank(DecoderDB, "VP"),
#     # decodersForBank(DecoderDB, "UT"),
#     decodersForBank(DecoderDB, "FTCluster"),
# ]
# UT = STOfflinePosition('ToolSvc.UTClusterPosition')
# UT.DetType = "UT"
# decodingSeq.Members += [d.setup() for x in decs for d in x]

vp_sequence = GaudiSequencer('PrPixelStoreClusters_Seq')
vp_sequence.Members.append(PrPixelStoreClusters())

# ft_sequence = GaudiSequencer('FTRawBankDecoder_Seq')
# from Configurables import FTRawBankDecoder
# ft_sequence.Members.append(FTRawBankDecoder())
# from Configurables import VPClustering
# vp_clustering = VPClustering()
# sequence = GaudiSequencer('MyGaudiSequencer')
# sequence.Members.append(vp_clustering)

# from Configurables import DecodeRawEvent
# DecodeRawEvent().DataOnDemand = True

# from Configurables import DigiConf
# DigiConf().Detectors = ['VP', 'UT', 'FT', 'Rich1Pmt', 'Rich2Pmt', 'Spd', 'Prs', 'Ecal', 'Hcal', 'Muon', 'Magnet']
# DigiConf().EnableUnpack = True

appConf = ApplicationMgr()
appConf.ExtSvc += ['ToolSvc', 'DataOnDemandSvc']


appConf.TopAlg += [vp_sequence]

appMgr = GaudiPython.AppMgr()
evt = appMgr.evtsvc()

poca = appMgr.toolsvc().create('TrajPoca', interface='ITrajPoca')
extrap = appMgr.toolsvc().create('TrackParabolicExtrapolator', interface='ITrackExtrapolator')
fitterTool = Panoramix.getTool('TrackMasterFitter', 'ITrackFitter')

appMgr.run(1)

# if not evt['/Event/Rec/Header']:
#     break

tracks = list(evt['Rec/Track/Best'])
track = tracks[0]

# LHCb Tracks appear to have the following states
# > Downstream BegRich2               FirstMeasurement
# > Long       BegRich2 ClosestToBeam FirstMeasurement
# > Ttrack     BegRich2               FirstMeasurement
# > Upstream            ClosestToBeam FirstMeasurement
# > Velo                ClosestToBeam
state_to_use = {
    ROOT.LHCb.Track.Velo: ROOT.LHCb.State.ClosestToBeam,
    ROOT.LHCb.Track.Downstream: ROOT.LHCb.State.FirstMeasurement,
    ROOT.LHCb.Track.Long: ROOT.LHCb.State.FirstMeasurement,
    ROOT.LHCb.Track.Ttrack: ROOT.LHCb.State.FirstMeasurement,
    ROOT.LHCb.Track.Upstream: ROOT.LHCb.State.FirstMeasurement,
}


def find_cluster(hit):
    assert hit.isVP()
    for c in evt['/Event/Raw/VP/Clusters']:
        if hit.vpID().channelID() == c.channelID().channelID():
            return c
    raise ValueError()


for track in evt['Rec/Track/Best']:
    # Find the state to propagate from
    state = track.stateAt(state_to_use[track.type()])
    assert state
    # TODO use track.closestState()????
    for hit in track.lhcbIDs():
        if not hit.isVP():
            continue
        c = find_cluster(hit)
        my_state = state.clone()
        assert extrap.propagate(my_state, c.z())
        apoint = my_state.position()
        adirec = my_state.slopes()
        traj = LineTraj(apoint, adirec, Range(-1000., 1000.))
        dis = XYZVector()
        s = Double(0.1)
        a = Double(0.0005)
        assert poca.minimize(traj, s, XYZPoint(c.x(), c.y(), c.z()), dis, a)
        # p_ontrack = traj.position(s)
        # print(success.isFailure() > 0)
        ip = dis.r()
        print(c.z(), ip, dis.x(), dis.y(), dis.z(), sep='\t')
