from Configurables import L0Conf
from Configurables import NTupleSvc
from Configurables import PrChecker2
from Configurables import LoKi__Hybrid__MCTool
from Gaudi.Configuration import GaudiSequencer

# As we haven't ran Moore
L0Conf().EnsureKnownTCK = False

# Required to avoid Loki issues when running PrChecker2
myFactory = LoKi__Hybrid__MCTool("MCHybridFactory")
myFactory.Modules = ["LoKiMC.decorators"]
PrChecker2("PrChecker2").addTool(myFactory)

GaudiSequencer("CheckPatSeq").Members = [
    "PrChecker",
    "PrChecker2",
    "TrackIPResolutionChecker",
    "TrackIPResolutionCheckerNT",
    "VPClusterMonitor"
]

NTupleSvc().Output += ["FILE1 DATAFILE='Brunel-tuples.root' TYP='ROOT' OPT='NEW'"]
