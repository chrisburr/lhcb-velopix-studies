import os
from os.path import join, isdir

# Not needed but keeps flake8 happy
from Ganga.GPI import (
    Job, Local, Dirac, prepareGaudiExec, SplitByFiles,
    TaskChainInput, DaVinci, LocalFile, GaudiExec, DiracFile
)

# Add Panoramix to cmtuser if needed
panoramix_dir = join(os.environ['HOME'], 'cmtuser', 'PanoramixDev_v23r2p2')
if not isdir(panoramix_dir):
    prepareGaudiExec('Panoramix', 'v23r2p2')

# Configure Panoramix
panoramix = GaudiExec()
panoramix.directory = panoramix_dir
panoramix.useGaudiRun = False
panoramix.options = ['panoramix_options.py']

# Make the LHCbTransform for panoramix
panoramix_job = Job(
    name='Panoramix',
    application=panoramix,
    splitter=None,
    backend=Local(),
    outputfiles=[LocalFile('*.root'), LocalFile('*.png')],
)
