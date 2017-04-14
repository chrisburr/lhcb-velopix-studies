from __future__ import print_function

from multiprocessing.pool import ThreadPool
from os import makedirs
from os.path import basename, isdir, isfile, join
import subprocess

from Ganga.GPI import jobs

assert modified

def download_hists(lfn, outdir):
    process = subprocess.Popen(
        'lb-run LHCbDirac dirac-dms-get-file '+lfn,
        shell=True, stdout=subprocess.PIPE, cwd=outdir
    )
    returncode = process.wait()
    print('Downloaded:', lfn, returncode)


tp = ThreadPool(64)

for j in jobs:
    scenario = j.comment[:-len(' reconstruction ')]
    outdir = join('output_final/scenarios', scenario, 'hists')
    if not isdir(outdir):
        makedirs(outdir)
    for sj in j.subjobs:
        if sj.status != 'completed' or sj.id not in jids:
            continue
        for f in sj.outputfiles:
            _outdir = join(outdir, str(sj.id))
            if not isdir(_outdir):
                makedirs(_outdir)
            if isfile(join(_outdir, basename(f.lfn))):
                print('Skipping', j.id, sj.id, f.lfn)
            else:
                tp.apply_async(download_hists, (f.lfn, _outdir))

tp.close()
tp.join()
