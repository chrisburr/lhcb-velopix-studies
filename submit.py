import os
from os.path import join, isdir

# Not needed but keeps flake8 happy
from Ganga.GPI import (
    LHCbTask, LHCbTransform, Local, Dirac, prepareGaudiExec, SplitByFiles,
    TaskChainInput, DaVinci, LocalFile, BKQuery, GaudiExec, DiracFile
)

# Config
APPCONFIGOPTS = "/afs/cern.ch/lhcb/software/releases/DBASE/AppConfig/v3r312/options"  # NOQA
BOOKEEPING_PATH = "/MC/Upgrade/Beam7000GeV-Upgrade-MagDown-Nu7.6-Pythia8/Sim09a-Upgrade/27163002/XDIGI"  # NOQA

# Make the LHCbTask
task = LHCbTask(float=8, name='LHCb hybrid distortion studies')

# Add Brunel to cmtuser if needed
brunel_dir = join(os.environ['HOME'], 'cmtuser', 'BrunelDev_v51r1')
if not isdir(brunel_dir):
    brunel = prepareGaudiExec('Brunel', 'v51r1')

# Add Brunel to cmtuser if needed
davinci_dir = join(os.environ['HOME'], 'cmtuser', 'DaVinciDev_v41r2')
if not isdir(davinci_dir):
    brunel = prepareGaudiExec('DaVinci', 'v41r2')

# Configure Brunel
brunel = GaudiExec()
brunel.directory = brunel_dir
brunel.options = [
    join(APPCONFIGOPTS, 'Brunel/MC-WithTruth.py'),
    join(APPCONFIGOPTS, 'Brunel/Brunel-Upgrade-Baseline-20150522.py'),
    join(APPCONFIGOPTS, 'Brunel/xdst.py'),
    'brunel_options.py'
]

# Configure DaVinci
davinci = GaudiExec()
davinci.directory = davinci_dir
davinci.options = ['davinci_options.py']

# Make the LHCbTransform for brunel
brunel_transform = LHCbTransform(
    name='Reconstruction',
    application=brunel,
    splitter=SplitByFiles(filesPerJob=1, ignoremissing=True),
    outputfiles=[DiracFile('*.xdst')],
)
task.appendTransform(brunel_transform)

bk_query = BKQuery(path=BOOKEEPING_PATH)
brunel_transform.addInputData(bk_query.getDataset())

# Make the LHCbTransform for davinci
davinci_transform = LHCbTransform(
    name='DaVinci',
    application=davinci,
    splitter=SplitByFiles(filesPerJob=1),
    outputfiles=[DiracFile('*.root')],
)
task.appendTransform(davinci_transform)

d = TaskChainInput()
d.include_file_mask = ['\.(mdst|dst|gen|digi|sim|xdst)$']
d.input_trf_id = brunel_transform.getID()
davinci_transform.addInputData(d)

for transform in task.transforms:
    transform.backend = Dirac()
    # transform.delete_chain_input = True
    transform.abort_loop_on_submit = False
    transform.submit_with_threads = True
    transform.files_per_unit = 10
task.run()
