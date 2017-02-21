#!/usr/bin/env bash

# Put bash in to strict mode
set -xeuo pipefail

function make_scenario_with_sigma {
    SCENARIO="$1"
    X_DIST="$2"
    Y_DIST="$3"
    SIGMA="$4"

    ./assets/build_alignment.py \
        --basedir="output/scenarios/$SCENARIO" \
        --x-distortion="$X_DIST" \
        --y-distortion="$Y_DIST" \
        --sigma="$SIGMA"

    lb-run LHCb/latest copy_files_to_db.py \
        -c "sqlite_file:output/scenarios/$SCENARIO/Alignment_SIMCOND.db/SIMCOND" \
        -s "output/scenarios/$SCENARIO/SIMCOND"
}

function make_scenario {
    make_scenario_with_sigma "$1" "$2" "$3" 0
    make_scenario_with_sigma "${1}_sigma=0.02" "$2" "$3" 0.02
    make_scenario_with_sigma "${1}_sigma=0.05" "$2" "$3" 0.05
    make_scenario_with_sigma "${1}_sigma=0.1" "$2" "$3" 0.1
    make_scenario_with_sigma "${1}_sigma=0.2" "$2" "$3" 0.2
}

make_scenario "tip_x=0um_y=-10000um" 0 -10000
make_scenario "tip_x=0um_y=-5000um" 0 -5000
make_scenario "tip_x=0um_y=-2000um" 0 -2000
make_scenario "tip_x=0um_y=-1000um" 0 -1000
make_scenario "tip_x=0um_y=-500um" 0 -500
make_scenario "tip_x=0um_y=-100um" 0 -100
make_scenario_with_sigma "Nominal" 0 0 0
make_scenario "tip_x=0um_y=+100um" 0 100
make_scenario "tip_x=0um_y=+500um" 0 500
make_scenario "tip_x=0um_y=+1000um" 0 1000
make_scenario "tip_x=0um_y=+2000um" 0 2000
make_scenario "tip_x=0um_y=+5000um" 0 5000
make_scenario "tip_x=0um_y=+10000um" 0 10000

make_scenario "tip_x=-10000um_y=0um" -10000 0
make_scenario "tip_x=-5000um_y=0um" -5000 0
make_scenario "tip_x=-2000um_y=0um" -2000 0
make_scenario "tip_x=-1000um_y=0um" -1000 0
make_scenario "tip_x=-500um_y=0um" -500 0
make_scenario "tip_x=-100um_y=0um" -100 0
make_scenario "tip_x=+100um_y=0um" 100 0
make_scenario "tip_x=+500um_y=0um" 500 0
make_scenario "tip_x=+1000um_y=0um" 1000 0
make_scenario "tip_x=+2000um_y=0um" 2000 0
make_scenario "tip_x=+5000um_y=0um" 5000 0
make_scenario "tip_x=+10000um_y=0um" 10000 0

make_scenario "tip_x=100um_y=-500um" -500 100
make_scenario "tip_x=100um_y=-100um" -100 100
make_scenario "tip_x=100um_y=+100um" 100 100
make_scenario "tip_x=100um_y=+500um" 500 100

make_scenario "tip_x=-100um_y=-500um" -500 -100
make_scenario "tip_x=-100um_y=-100um" -100 -100
make_scenario "tip_x=-100um_y=+100um" 100 -100
make_scenario "tip_x=-100um_y=+500um" 500 -100

