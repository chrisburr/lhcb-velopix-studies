##############################################################################
# File for running Brunel on MC data and saving all MC Truth
# DataType should be set separately
#
# Syntax is:
# gaudirun.py Brunel/MC-WithTruth.py Conditions/<someTag>.py <someDataFiles>.py
##############################################################################

from Configurables import Brunel

Brunel().InputType = "DIGI" # implies also Brunel().Simulation = True
Brunel().WithMC    = True   # implies also Brunel().Simulation = True

##############################################################################
