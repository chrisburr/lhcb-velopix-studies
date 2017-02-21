import os
from os.path import join, isdir

# Not needed but keeps flake8 happy
from Ganga.GPI import (
    Local, Dirac, prepareGaudiExec, SplitByFiles, LocalFile, BKQuery,
    GaudiExec, DiracFile, Job
)

# Config
APPCONFIGOPTS = "/afs/cern.ch/lhcb/software/releases/DBASE/AppConfig/v3r312/options"  # NOQA
BOOKEEPING_PATH = "/MC/Upgrade/Beam7000GeV-Upgrade-MagDown-Nu7.6-Pythia8/Sim09a-Upgrade/27163002/XDIGI"  # NOQA
RUN_LOCAL = False

# Add Brunel to cmtuser if needed
brunel_dir = join(os.environ['HOME'], 'cmtuser', 'BrunelDev_v51r1')
if not isdir(brunel_dir):
    brunel = prepareGaudiExec('Brunel', 'v51r1')

# Configure Brunel
brunel = GaudiExec()
brunel.directory = brunel_dir
brunel.options = [
    join(APPCONFIGOPTS, 'Brunel/MC-WithTruth.py'),
    join(APPCONFIGOPTS, 'Brunel/Brunel-Upgrade-Baseline-20150522.py'),
    join(APPCONFIGOPTS, 'Brunel/xdst.py'),
    'brunel_options.py'
]
brunel.extraOpts += '''
from Configurables import Brunel
Brunel().EvtMax = {evt_max}
'''.format(evt_max=[-1, 1][RUN_LOCAL])

# Configure the corresponding Job
brunel_job = Job(
    name='VP hybrid distortions',
    comment='Nominal reconstruction'+['', ' (Local)'][RUN_LOCAL],
    application=brunel,
    splitter=SplitByFiles(filesPerJob=1, ignoremissing=True),
    parallel_submit=True
)

dataset = BKQuery(path=BOOKEEPING_PATH).getDataset()

if RUN_LOCAL:
    brunel_job.backend = Local()
    brunel_job.outputfiles = [LocalFile('*.xdst'), LocalFile('*.root')]
    brunel_job.inputdata = dataset[:8]
else:
    brunel_job.backend = Dirac()
    brunel_job.outputfiles = [DiracFile('*.xdst'), DiracFile('*.root')]
    brunel_job.inputdata = dataset

brunel_job.submit()
