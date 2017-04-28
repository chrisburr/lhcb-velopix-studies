from Configurables import Brunel
from Configurables import CondDB
from Configurables import LHCbApp
from Configurables import L0Conf
from Gaudi.Configuration import GaudiSequencer


Brunel().InputType = "DIGI"
Brunel().WithMC = True
CondDB().Upgrade = True
Brunel().Detectors = ['VP', 'UT', 'FT', 'Rich1Pmt', 'Rich2Pmt', 'Ecal', 'Hcal', 'Muon', 'Magnet', 'Tr']
Brunel().DataType = "Upgrade"
Brunel().OutputType = 'XDST'

# As we haven't ran Moore
L0Conf().EnsureKnownTCK = False

GaudiSequencer("CheckPatSeq").Members = [
    "PrChecker",
    "TrackIPResolutionChecker",
    "VPClusterMonitor"
]

LHCbApp().DDDBtag = "dddb-20170301"
LHCbApp().CondDBtag = "sim-20170301-vc-md100"
