from Configurables import Brunel
from Configurables import CondDB
from Configurables import CondDBAccessSvc
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

CondDB().addLayer(dbFile="check_positions/DDDB.db", dbName="DDDB")
CondDB().addLayer(dbFile="check_positions/SIMCOND.db", dbName="SIMCOND")
alignment_conditions = CondDBAccessSvc("AlignmentConditions")
alignment_conditions.ConnectionString = "sqlite_file:check_positions/Alignment_SIMCOND.db/SIMCOND"
CondDB().addLayer(alignment_conditions)
