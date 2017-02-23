from __future__ import print_function

from multiprocessing.pool import ThreadPool
from os import listdir, makedirs
from os.path import isdir, join
import subprocess

from Ganga.GPI import jobs


def download_hists(lfn, outdir):
    if not isdir(outdir):
        makedirs(outdir)
    process = subprocess.Popen(
        'lb-run LHCbDirac dirac-dms-get-file '+lfn,
        shell=True, stdout=subprocess.PIPE, cwd=outdir
    )
    returncode = process.wait()
    print('Downloaded:', lfn, returncode)


tp = ThreadPool(64)

for j in jobs:
    scenario = j.comment[:-len(' reconstruction ')]
    outdir = join('output/scenarios', scenario, 'hists')
    if not isdir(outdir):
        makedirs(outdir)
    for sj in j.subjobs:
        if sj.status != 'completed':
            continue
        for f in sj.outputfiles:
            if not f.lfn.endswith('.root'):
                continue
            _outdir = join(outdir, str(sj.id))
            if isdir(_outdir) and listdir(_outdir):
                print('Skipping', f.lfn)
            else:
                tp.apply_async(download_hists, (f.lfn, _outdir))

tp.close()
tp.join()
