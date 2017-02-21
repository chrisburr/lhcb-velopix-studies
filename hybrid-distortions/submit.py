# [SublimeLinter flake8-max-line-length:100]
import os
from os.path import join, isdir

# Not needed but keeps flake8 happy
from Ganga.GPI import (
    Local, Dirac, prepareGaudiExec, SplitByFiles, LocalFile, BKQuery,
    GaudiExec, DiracFile, Job
)

# Config
BOOKEEPING_PATH = "/MC/Upgrade/Beam7000GeV-Upgrade-MagDown-Nu7.6-Pythia8/Sim09a-Upgrade/27163002/XDIGI"  # NOQA
RUN_LOCAL = False


def get_brunel(custom_db=False):
    # Add Brunel to cmtuser if needed
    brunel_dir = join(os.environ['HOME'], 'cmtuser', 'BrunelDev_v51r1')
    if not isdir(brunel_dir):
        brunel = prepareGaudiExec('Brunel', 'v51r1')

    # Configure Brunel
    brunel = GaudiExec()
    brunel.directory = brunel_dir
    brunel.options = [
        'options/MC-WithTruth.py',
        'options/Brunel-Upgrade-Baseline-20150522.py',
        'options/xdst.py',
        'options/brunel_options.py'
    ]

    if custom_db:
        brunel.extraOpts = (
            'from Configurables import CondDB'
            'from Configurables import CondDBAccessSvc'
            'CondDB().addLayer(dbFile="DDDB.db", dbName="DDDB")'
            'CondDB().addLayer(dbFile="SIMCOND.db", dbName="SIMCOND")'
            'alignment_conditions = CondDBAccessSvc("AlignmentConditions")'
            'alignment_conditions.ConnectionString = "sqlite_file:Alignment_SIMCOND.db/SIMCOND"'
            'CondDB().addLayer(alignment_conditions)'
        )
    else:
        brunel.extraOpts = (
            'from Configurables import Brunel\n'
            'from Configurables import LHCbApp\n'
            'LHCbApp().DDDBtag = "dddb-20160304"\n'
            'LHCbApp().CondDBtag = "sim-20150716-vc-md100"\n'
        )

    return brunel


def submit_job(brunel_app, reco_type, input_files=None, local=RUN_LOCAL):
    # Set EvtMax depending on if this is a local job
    brunel_app.extraOpts += 'from Configurables import Brunel\n'
    brunel_app.extraOpts += 'Brunel().EvtMax = {0}'.format(2*int(local)-1)

    # Configure the corresponding Job
    job = Job(
        name='VP hybrid distortions',
        comment='{reco_type} reconstruction {suffix}'
                .format(reco_type=reco_type, suffix=['', '(local)'][local]),
        application=brunel_app,
        splitter=SplitByFiles(filesPerJob=1, ignoremissing=True),
        parallel_submit=True
    )

    dataset = BKQuery(path=BOOKEEPING_PATH).getDataset()

    if local:
        job.backend = Local()
        job.outputfiles = [LocalFile('*.xdst'), LocalFile('*.root')]
        job.inputdata = dataset[:8]
    else:
        job.backend = Dirac()
        job.outputfiles = [DiracFile('*.xdst'), DiracFile('*.root')]
        job.inputdata = dataset

    job.inputfiles = input_files or []

    job.submit()


brunel = get_brunel(custom_db=False)
submit_job(brunel, 'Original DB')

# brunel = get_brunel(custom_db=True)
# submit_job(brunel, 'Nominal', input_files=[])
