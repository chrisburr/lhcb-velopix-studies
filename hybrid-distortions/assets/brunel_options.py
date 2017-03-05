from Configurables import L0Conf
from Gaudi.Configuration import GaudiSequencer

# As we haven't ran Moore
L0Conf().EnsureKnownTCK = False

GaudiSequencer("CheckPatSeq").Members = [
    "PrChecker",
    "TrackIPResolutionChecker",
    "TrackIPResolutionCheckerNT",
    "VPClusterMonitor"
]
