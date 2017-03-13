# Hybrid distortion studies
Simulation of the effects of the observed distortions of the velopix modules

## Running
```bash
./patch_databases.sh
./make_alignment_scenarios.sh
lb-run Ganga ganga
# > execfile('submit.py')
# Once jobs have finished (assuming no other jobs are present in ganga)
# > execfile('download_hists.py')
# Edit make_resolution_plots.py to make the desired plots
./make_resolution_plots.py
# And to make the msgpack files for running the notebook
lb-run Panoramix/latest python read_xdst.py $SCENARIO
```

## Useful links

 - [https://lbtwiki.cern.ch/bin/view/VELO/VELOUpgraderndWP5](https://lbtwiki.cern.ch/bin/view/VELO/VELOUpgraderndWP5)
 - [https://cds.cern.ch/record/1624070/files/LHCB-TDR-013.pdf](https://cds.cern.ch/record/1624070/files/LHCB-TDR-013.pdf)
