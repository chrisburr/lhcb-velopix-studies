# [SublimeLinter flake8-max-line-length:100]
from __future__ import print_function

from Configurables import Escher, RecSysConf, LHCbApp, RecMoniConf
from GaudiKernel.ProcessJobOptions import importOptions
from Configurables import CondDB, CondDBAccessSvc

detectors = ['VP', 'UT', 'FT', 'Magnet', 'Tr']

importOptions('$STDOPTS/PreloadUnits.opts')

LHCbApp().Simulation = True
LHCbApp().DataType = 'Upgrade'
CondDB().Upgrade = True

LHCbApp().Detectors = detectors


CondDB().addLayer(dbFile='check_positions/DDDB.db', dbName='DDDB')
CondDB().addLayer(dbFile='check_positions/SIMCOND.db', dbName='SIMCOND')
alignment_conditions = CondDBAccessSvc('AlignmentConditions')
alignment_conditions.ConnectionString = 'sqlite_file:./check_positions/Alignment_SIMCOND.db/SIMCOND'
CondDB().addLayer(alignment_conditions)

CondDB().LoadCALIBDB = 'HLT1'

Escher().InputType = "DIGI"
Escher().Kalman = True
Escher().Millepede = False
Escher().EvtMax = -1
Escher().MoniSequence = []
Escher().RecoSequence = ["Decoding", "VP", "VELOPIX", "Tr", "Vertex"]
Escher().WithMC = True
Escher().Simulation = True
Escher().DataType = 'Upgrade'
Escher().Upgrade = True
RecSysConf().Detectors = detectors
RecMoniConf().Detectors = detectors

Escher().ExpertTracking = ["kalmanSmoother"]
