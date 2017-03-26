##############################################################################
# File for running VP alignment on simulated Data
#
# Syntax is:
#
#   gaudirun.py $ESCHEROPTS/AlignVeloSensors.py $ESCHEROPTS/2008-MC-Files.py
#   gaudirun.py $ESCHEROPTS/AlignVeloSensors.py $ESCHEROPTS/DC06-Files.py
#
#   $ESCHEROPTS/gaudiiter.py -n 3 -e 1000 $ESCHEROPTS/AlignVeloSensors.py $ESCHEROPTS/2008-MC-Files.py
#
##############################################################################
import os

from Configurables import Escher, TrackSys, RecSysConf, LHCbApp, DstConf, RecMoniConf
from GaudiKernel.ProcessJobOptions import importOptions
from Configurables import CondDB, CondDBAccessSvc
from Configurables import GaudiSequencer
from Configurables import PrPixelTracking, PrPixelStoreClusters, PrLHCbID2MCParticle
from Configurables import TAlignment
from TAlignment.Alignables import Alignables  # *
from TAlignment.TrackSelections import *
from Configurables import AlignAlgorithm
from Configurables import TrackContainerCopy, TrackSelector
from Configurables import VPTrackSelector
from TrackFitter.ConfiguredFitters import *
from Gaudi.Configuration import appendPostConfigAction
from TAlignment.SurveyConstraints import SurveyConstraints  # *
from GaudiConf import IOHelper
from Configurables import CaloDigitConf, CaloProcessor, GlobalRecoConf


print os.listdir(os.getcwd())


importOptions('$STDOPTS/PreloadUnits.opts')

# Load the velo conditions
CondDB().addLayer(dbFile="/pc2014-data3/cburr/hybrid-distortions/try_aligning/DDDB.db", dbName="DDDB")
CondDB().addLayer(dbFile="/pc2014-data3/cburr/hybrid-distortions/try_aligning/SIMCOND.db", dbName="SIMCOND")
alignment_conditions = CondDBAccessSvc("AlignmentConditions")
alignment_conditions.ConnectionString = "sqlite_file:/pc2014-data3/cburr/hybrid-distortions/try_aligning/Alignment_SIMCOND.db/SIMCOND"
CondDB().addLayer(alignment_conditions)

LHCbApp().Simulation = True
LHCbApp().DataType = 'Upgrade'
CondDB().Upgrade = True

detectors = ['VP', 'UT', 'FT', 'Rich1Pmt', 'Rich2Pmt', 'Ecal', 'Hcal', 'Muon', 'Magnet', 'Tr']
LHCbApp().Detectors = detectors

CondDB().LoadCALIBDB = 'HLT1'

Escher().InputType = "DIGI"
Escher().Kalman = True
Escher().Millepede = False
# Escher().TrackContainer = "Rec/Track/Velo" # Velo, VeloR, Long, Upstream, Downstream, Ttrack, Muon or Calo
Escher().EvtMax = -1
Escher().MoniSequence = []
Escher().RecoSequence = ["Decoding", "VP", "VELOPIX", "Tr", "Vertex", "CALO", "PROTO"]
Escher().WithMC = True
Escher().Simulation = True
Escher().DataType = 'Upgrade'
Escher().Upgrade = True
RecSysConf().Detectors = detectors
RecMoniConf().Detectors = detectors

Escher().ExpertTracking = ["kalmanSmoother"]


TrackSys().TrackExtraInfoAlgorithms = []
TrackSys().DataType = 'Upgrade'
TrackSys().Simulation = True
TrackSys().WithMC = True
#TrackSys().TrackTypes   = ["Velo"]
TrackSys().TrackPatRecAlgorithms = ["VP", "Forward", "TsaSeed", "Match", "Downstream"]
DstConf().Detectors = detectors


hvpseq = GaudiSequencer("VPSeq")
prLHCbID2mc = PrLHCbID2MCParticle()
prPixTr = PrPixelTracking()
prPixStCl = PrPixelStoreClusters()

hvpseq.Members += [prPixStCl, prPixTr, prLHCbID2mc]


AlignAlgorithm("Alignment").ForcedInitialTime = 1

elements = Alignables()
elements.VPModules("TxTyTzRxRyRz")
# elements.VPLeft("TxTy")
# elements.VPRight("TxTyRz")
# constraints = ["Rz","Ry","Rx","Szx","Szy","SRz"]
constraints = ["Tx", "Ty", "Szx", "Szy", "Rz", "SRz"]

# constraints = []
constraints.append("VPFixModule10 : VP/VPLeft/Module10WithSupport: Tx Ty Tz Rx Ry Rz")
constraints.append("VPFixModule11 : VP/VPRight/Module11WithSupport: Tx Ty Tz Rx Ry Rz")
constraints.append("VPFixModule40 : VP/VPLeft/Module40WithSupport: Tx Ty Tz Rx Ry Rz")
constraints.append("VPFixModule41 : VP/VPRight/Module41WithSupport: Tx Ty Tz Rx Ry Rz")
# constraints = []
print "aligning elements ", elements
trackRefitSeq = GaudiSequencer("TrackRefitSeq")

# create a track list for tracks with velo hits
velotrackselector = TrackContainerCopy("TracksWithVeloHits",
                                       inputLocation="Rec/Track/Best",
                                       outputLocation="Rec/Track/TracksWithVeloHits",
                                       Selector=TrackSelector())

# refit the tracks in that list
velotrackrefitter = ConfiguredEventFitter(Name="TracksWithVeloHitsFitter",
                                          TracksInContainer="Rec/Track/TracksWithVeloHits",
                                          FieldOff=True)
velotrackrefitter.Fitter.MeasProvider.IgnoreIT = True
velotrackrefitter.Fitter.MeasProvider.IgnoreOT = True
velotrackrefitter.Fitter.MeasProvider.IgnoreTT = True
velotrackrefitter.Fitter.MeasProvider.IgnoreMuon = True
velotrackrefitter.Fitter.MeasProvider.IgnoreUT = True
velotrackrefitter.Fitter.MakeNodes = True
velotrackrefitter.Fitter.MakeMeasurements = True

trackRefitSeq.Members += [velotrackselector, velotrackrefitter]


def redefinefilters():
        GaudiSequencer("RecoTrSeq").Members += [trackRefitSeq]


appendPostConfigAction(redefinefilters)


class myVPTracksOverlap(TrackRefiner):
    def __init__(self, Name="VPOverlapTracks", InputLocation="Rec/Track/TracksWithVeloHits", Fitted=True):
        TrackRefiner.__init__(self, Name=Name, InputLocation=InputLocation, Fitted=Fitted)

    def configureSelector(self, a):
        a.Selector = VPTrackSelector()
        a.Selector.MinHitsASide = 1
        a.Selector.MinHitsCSide = 1
        a.Selector.TrackTypes = ["Velo", "Long"]


class myVPTracks(TrackRefiner):
    def __init__(self, Name="VPOverlapTracks", InputLocation="Rec/Track/TracksWithVeloHits", Fitted=True):
        TrackRefiner.__init__(self, Name=Name, InputLocation=InputLocation, Fitted=Fitted)

    def configureSelector(self, a):
        a.Selector = VPTrackSelector()
        a.Selector.TrackTypes = ["Long"]
        a.Selector.MinHits = 5
        a.Selector.MinPCut = 5000
        a.Selector.MaxPCut = 200000
        a.Selector.MinPtCut = 200

        if self._fitted:
            a.Selector.MaxChi2Cut = 5
            a.Selector.MaxChi2PerDoFMatch = 5
            a.Selector.MaxChi2PerDoFVelo = 5
            a.Selector.MaxChi2PerDoFDownstream = 5


class VPBackwards(TrackRefiner):
    def __init__(self, Name="VPTracks", InputLocation="Rec/Track/Best", Fitted=True):
        TrackRefiner.__init__(self, Name=Name, InputLocation=InputLocation, Fitted=Fitted)

    def configureSelector(self, a):
        a.Selector = VPTrackSelector()
        a.Selector.TrackTypes = ["Backward"]

        a.Selector.MinHits = 5
        if self._fitted:
            a.Selector.MaxChi2Cut = 5


TAlignment().ElementsToAlign = list(elements)
TAlignment().TrackLocation = "Rec/Track/Best"
TAlignment().VertexLocation = ""  # Rec/Vertex/Primary"
TAlignment().Constraints = constraints
TAlignment().TrackSelections = [myVPTracks(), VPBackwards()]
TAlignment().WriteCondSubDetList = ['VP']
TAlignment().EigenValueThreshold = 100
TAlignment().UsePreconditioning = True
TAlignment().UseLocalFrame = True
# include survey constraints

surveyconstraints = SurveyConstraints()
surveyconstraints.VP()

# Convert Calo ReadoutStatus to ProcStatus
caloBanks = GaudiSequencer("CaloBanksHandler")
caloDetectors = [det for det in ['Spd', 'Prs', 'Ecal', 'Hcal'] if det in detectors]
CaloDigitConf(ReadoutStatusConvert=True, Sequence=caloBanks, Detectors=caloDetectors)
GaudiSequencer("EscherSequencer").Members += [caloBanks]

# New NoSPDPRS switches
noSPDPRS = False
if [det for det in ['Spd', 'Prs'] if det not in detectors]:
    noSPDPRS = True
CaloProcessor().setProp("NoSpdPrs", noSPDPRS)
GlobalRecoConf().setProp("NoSpdPrs", noSPDPRS)


def doMyChanges():
    GaudiSequencer("HltFilterSeq").Members = []


appendPostConfigAction(doMyChanges)

# indir = '/afs/cern.ch/work/c/chombach/public/VP/BooleOutput/'
# inputdata = []
# files = os.listdir(indir)
# for file in files:
#    inputdata.append("DATAFILE='PFN:"+indir+file+"'")

# inputFiles = ['/eos/lhcb/user/c/chombach/ganga/2744/0/BrunelTest.xdst']
# for i in range(209):
#     # if BEAMGAS:
#     #     inputdata.append("PFN:root://eoslhcb.cern.ch//eos/lhcb/user/c/chombach/ganga/5068/%i/BooleOutput.digi-Extended.digi" % i)
#     # else:
#     #     inputdata.append("PFN:root://eoslhcb.cern.ch//eos/lhcb/user/c/chombach/ganga/2745/%i/BooleOutput.digi-Extended.digi" % i)
#     inputFiles = inputdata

IOHelper('ROOT').inputFiles([
    'PFN:root://ccdcacli067.in2p3.fr:1094/pnfs/in2p3.fr/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000013_1.xdigi',
    'PFN:root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000010_1.xdigi',
    # 'PFN:file:///storage/gpfs_lhcb/lhcb/disk/MC/Upgrade/XDIGI/00052242/0000/00052242_00000046_1.xdigi',
    # 'PFN:root://clhcbstager.ads.rl.ac.uk//castor/ads.rl.ac.uk/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000017_1.xdigi?svcClass=lhcbDst',
    'PFN:root://lhcb-sdpd13.t1.grid.kiae.ru:1094/t1.grid.kiae.ru/data/lhcb/lhcbdisk/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000008_1.xdigi',
    'PFN:root://clhcbstager.ads.rl.ac.uk//castor/ads.rl.ac.uk/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000040_1.xdigi?svcClass=lhcbDst',
    'PFN:root://lhcb-sdpd13.t1.grid.kiae.ru:1094/t1.grid.kiae.ru/data/lhcb/lhcbdisk/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000029_1.xdigi',
    'PFN:root://lhcb-sdpd17.t1.grid.kiae.ru:1094/t1.grid.kiae.ru/data/lhcb/lhcbdisk/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000055_1.xdigi',
    # 'PFN:file:///storage/gpfs_lhcb/lhcb/disk/MC/Upgrade/XDIGI/00052242/0000/00052242_00000033_1.xdigi',
    'PFN:root://ccdcacli067.in2p3.fr:1094/pnfs/in2p3.fr/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000031_1.xdigi',
    'PFN:root://door02.pic.es:1094/pnfs/pic.es/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000035_1.xdigi',
    'PFN:root://ccdcacli067.in2p3.fr:1094/pnfs/in2p3.fr/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000025_1.xdigi',
    'PFN:root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000006_1.xdigi',
    'PFN:root://door04.pic.es:1094/pnfs/pic.es/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000001_1.xdigi',
    'PFN:root://f01-080-125-e.gridka.de:1094/pnfs/gridka.de/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000048_1.xdigi',
    'PFN:root://ccdcacli067.in2p3.fr:1094/pnfs/in2p3.fr/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000023_1.xdigi',
    'PFN:root://mouse7.grid.surfsara.nl:1094/pnfs/grid.sara.nl/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000028_1.xdigi',
    'PFN:root://by27-3.grid.sara.nl:1094/pnfs/grid.sara.nl/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000003_1.xdigi',
    'PFN:root://bw32-8.grid.sara.nl:1094/pnfs/grid.sara.nl/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000018_1.xdigi',
    'PFN:root://f01-080-125-e.gridka.de:1094/pnfs/gridka.de/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000024_1.xdigi',
    'PFN:root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000012_1.xdigi',
    'PFN:root://f01-080-125-e.gridka.de:1094/pnfs/gridka.de/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000042_1.xdigi',
    # 'PFN:file:///storage/gpfs_lhcb/lhcb/disk/MC/Upgrade/XDIGI/00052242/0000/00052242_00000045_1.xdigi',
    'PFN:root://clhcbstager.ads.rl.ac.uk//castor/ads.rl.ac.uk/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000060_1.xdigi?svcClass=lhcbDst',
    'PFN:root://ccdcacli067.in2p3.fr:1094/pnfs/in2p3.fr/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000015_1.xdigi',
    'PFN:root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000047_1.xdigi',
    'PFN:root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000034_1.xdigi',
    'PFN:root://ccdcacli067.in2p3.fr:1094/pnfs/in2p3.fr/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000053_1.xdigi',
    'PFN:root://ccdcacli067.in2p3.fr:1094/pnfs/in2p3.fr/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000021_1.xdigi',
    'PFN:root://clhcbstager.ads.rl.ac.uk//castor/ads.rl.ac.uk/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000038_1.xdigi?svcClass=lhcbDst',
    'PFN:root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000050_1.xdigi',
    'PFN:root://mouse10.grid.surfsara.nl:1094/pnfs/grid.sara.nl/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000004_1.xdigi',
    'PFN:root://door04.pic.es:1094/pnfs/pic.es/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000007_1.xdigi',
    'PFN:root://ccdcacli067.in2p3.fr:1094/pnfs/in2p3.fr/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000059_1.xdigi',
    'PFN:root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000019_1.xdigi',
    'PFN:root://ccdcacli067.in2p3.fr:1094/pnfs/in2p3.fr/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000030_1.xdigi',
    'PFN:root://ccdcacli067.in2p3.fr:1094/pnfs/in2p3.fr/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000061_1.xdigi',
    'PFN:root://ccdcacli067.in2p3.fr:1094/pnfs/in2p3.fr/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000039_1.xdigi',
    'PFN:root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000044_1.xdigi',
    # 'PFN:file:///storage/gpfs_lhcb/lhcb/disk/MC/Upgrade/XDIGI/00052242/0000/00052242_00000020_1.xdigi',
    'PFN:root://clhcbstager.ads.rl.ac.uk//castor/ads.rl.ac.uk/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000022_1.xdigi?svcClass=lhcbDst',
    'PFN:root://f01-080-125-e.gridka.de:1094/pnfs/gridka.de/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000052_1.xdigi',
    'PFN:root://ccdcacli067.in2p3.fr:1094/pnfs/in2p3.fr/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000026_1.xdigi',
    'PFN:root://clhcbstager.ads.rl.ac.uk//castor/ads.rl.ac.uk/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000036_1.xdigi?svcClass=lhcbDst',
    # 'PFN:file:///storage/gpfs_lhcb/lhcb/disk/MC/Upgrade/XDIGI/00052242/0000/00052242_00000011_1.xdigi',
    'PFN:root://ccdcacli067.in2p3.fr:1094/pnfs/in2p3.fr/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000016_1.xdigi',
    'PFN:root://door02.pic.es:1094/pnfs/pic.es/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000049_1.xdigi',
    'PFN:root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000056_1.xdigi',
    'PFN:root://lhcb-sdpd4.t1.grid.kiae.ru:1094/t1.grid.kiae.ru/data/lhcb/lhcbdisk/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000014_1.xdigi',
    'PFN:root://clhcbstager.ads.rl.ac.uk//castor/ads.rl.ac.uk/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000054_1.xdigi?svcClass=lhcbDst',
    'PFN:root://clhcbstager.ads.rl.ac.uk//castor/ads.rl.ac.uk/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000009_1.xdigi?svcClass=lhcbDst',
    'PFN:root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000051_1.xdigi',
    'PFN:root://ccdcacli067.in2p3.fr:1094/pnfs/in2p3.fr/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000037_1.xdigi',
    'PFN:root://ccdcacli067.in2p3.fr:1094/pnfs/in2p3.fr/data/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000005_1.xdigi',
    'PFN:root://clhcbstager.ads.rl.ac.uk//castor/ads.rl.ac.uk/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000002_1.xdigi?svcClass=lhcbDst',
    'PFN:root://lhcb-sdpd18.t1.grid.kiae.ru:1094/t1.grid.kiae.ru/data/lhcb/lhcbdisk/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000057_1.xdigi',
    'PFN:root://f01-080-123-e.gridka.de:1094/pnfs/gridka.de/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000058_1.xdigi',
    'PFN:root://lhcb-sdpd6.t1.grid.kiae.ru:1094/t1.grid.kiae.ru/data/lhcb/lhcbdisk/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000043_1.xdigi',
    'PFN:root://clhcbstager.ads.rl.ac.uk//castor/ads.rl.ac.uk/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000027_1.xdigi?svcClass=lhcbDst',
    'PFN:root://clhcbstager.ads.rl.ac.uk//castor/ads.rl.ac.uk/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000032_1.xdigi?svcClass=lhcbDst',
    'PFN:root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/MC/Upgrade/XDIGI/00052242/0000/00052242_00000041_1.xdigi'
])
