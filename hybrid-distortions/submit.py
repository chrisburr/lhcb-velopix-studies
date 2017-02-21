# [SublimeLinter flake8-max-line-length:100]
from glob import glob
import os
from os.path import basename, dirname, isdir, join

# Not needed but keeps flake8 happy
from Ganga.GPI import (
    Local, Dirac, prepareGaudiExec, SplitByFiles, LocalFile, BKQuery,
    GaudiExec, DiracFile, Job
)

# Config
BOOKEEPING_PATH = "/MC/Upgrade/Beam7000GeV-Upgrade-MagDown-Nu7.6-Pythia8/Sim09a-Upgrade/27163002/XDIGI"  # NOQA
RUN_LOCAL = True

dataset = BKQuery(path=BOOKEEPING_PATH).getDataset()


def get_brunel(custom_db=False):
    # Add Brunel to cmtuser if needed
    brunel_dir = join(os.environ['HOME'], 'cmtuser', 'BrunelDev_v51r1')
    if not isdir(brunel_dir):
        brunel = prepareGaudiExec('Brunel', 'v51r1')

    # Configure Brunel
    brunel = GaudiExec()
    brunel.directory = brunel_dir
    brunel.options = [
        'assets/MC-WithTruth.py',
        'assets/Brunel-Upgrade-Baseline-20150522.py',
        'assets/xdst.py',
        'assets/brunel_options.py'
    ]

    if custom_db:
        brunel.extraOpts = (
            'from Configurables import CondDB\n'
            'from Configurables import CondDBAccessSvc\n'
            'CondDB().addLayer(dbFile="DDDB.db", dbName="DDDB")\n'
            'CondDB().addLayer(dbFile="SIMCOND.db", dbName="SIMCOND")\n'
            'alignment_conditions = CondDBAccessSvc("AlignmentConditions")\n'
            'alignment_conditions.ConnectionString = "sqlite_file:Alignment_SIMCOND.db/SIMCOND"\n'
            'CondDB().addLayer(alignment_conditions)\n'
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
    brunel_app.extraOpts += 'Brunel().EvtMax = 5'.format(2*int(local)-1)

    # Configure the corresponding Job
    job = Job(
        name='VP hybrid distortions',
        comment='{reco_type} reconstruction {suffix}'
                .format(reco_type=reco_type, suffix=['', '(local)'][local]),
        application=brunel_app,
        splitter=SplitByFiles(filesPerJob=1, ignoremissing=True),
        parallel_submit=True
    )

    if local:
        job.backend = Local()
        job.outputfiles = [LocalFile('*.xdst'), LocalFile('*.root')]
        job.inputdata = dataset[:1]
    else:
        job.backend = Dirac()
        job.outputfiles = [DiracFile('*.xdst'), DiracFile('*.root')]
        job.inputdata = dataset

    job.inputfiles = input_files or []

    job.submit()


# Submit a job using the nominal tags directly
brunel = get_brunel(custom_db=False)
submit_job(brunel, 'Original DB')

for db in glob('output/scenarios/*/Alignment_SIMCOND.db'):
    scenario_name = basename(dirname(db))
    brunel = get_brunel(custom_db=True)
    submit_job(brunel, scenario_name, input_files=[
        join(os.getcwd(), 'output/DDDB.db'),
        join(os.getcwd(), 'output/SIMCOND.db'),
        join(os.getcwd(), db)
    ])
