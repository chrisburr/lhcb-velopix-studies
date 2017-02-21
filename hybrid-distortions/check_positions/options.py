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
from __future__ import print_function

from Configurables import (Escher, TrackSys, RecSysConf, LHCbApp, DstConf, RecMoniConf)
from GaudiKernel.ProcessJobOptions import importOptions
from Configurables import CondDB, CondDBAccessSvc
from Configurables import DDDBConf
from Configurables import GaudiSequencer
from Configurables import PrPixelTracking, PrPixelStoreClusters, PrLHCbID2MCParticle
from Configurables import TAlignment
from Configurables import AlignAlgorithm
from Configurables import TrackContainerCopy, TrackSelector
from Configurables import VPTrackSelector
from Gaudi.Configuration import appendPostConfigAction
from Configurables import CaloDigitConf, CaloProcessor, GlobalRecoConf
from GaudiConf import IOHelper
from TAlignment.Alignables import Alignables
from TAlignment.TrackSelections import TrackRefiner
from TrackFitter.ConfiguredFitters import ConfiguredEventFitter
from TAlignment.SurveyConstraints import SurveyConstraints

import inspect
import os
import sys
sys.path.append(os.path.dirname(inspect.getfile(inspect.currentframe())))  # NOQA
import config


detectors = config.DETECTORS + ['Tr']

importOptions('$STDOPTS/PreloadUnits.opts')

LHCbApp().Simulation = True
LHCbApp().DataType = 'Upgrade'
CondDB().Upgrade = True

LHCbApp().Detectors = detectors


CondDB().addLayer(dbFile='./DDDB.db', dbName='DDDB')
CondDB().addLayer(dbFile='./SIMCOND.db', dbName='SIMCOND')
alignment_conditions = CondDBAccessSvc('AlignmentConditions')
alignment_conditions.ConnectionString = 'sqlite_file:./alignment_SIMCOND.db/SIMCOND'
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
