############################################################################
# File for running Brunel with all Baseline Upgrade detectors as of May 2015
############################################################################

from Configurables import Brunel, CondDB

CondDB().Upgrade = True

Brunel().Detectors = ['VP', 'UT', 'FT', 'Rich1Pmt', 'Rich2Pmt', 'Ecal', 'Hcal', 'Muon', 'Magnet', 'Tr']
Brunel().DataType = "Upgrade"
