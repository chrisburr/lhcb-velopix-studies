from Configurables import Brunel
from Configurables import LHCbApp
from Configurables import L0Conf

# Set up the databases
LHCbApp().DDDBtag = 'dddb-20160304'
LHCbApp().CondDBtag = 'sim-20150716-vc-md100'

# As we haven't ran Moore
L0Conf().EnsureKnownTCK = False

Brunel().EvtMax = -1
