#!/usr/bin/env bash

# Put bash in to strict mode
set -xeuo pipefail

function make_scenario {
    SCENARIO=$1
    X_DIST=$2
    Y_DIST=$3

    ./assets/build_alignment.py \
        --global-fn="output/scenarios/$SCENARIO/SIMCOND/Conditions/VP/Alignment/Global.xml" \
        --modules-fn="output/scenarios/$SCENARIO/SIMCOND/Conditions/VP/Alignment/Modules.xml" \
        --x-distortion="$X_DIST" \
        --y-distortion="$Y_DIST"

    lb-run LHCb/latest copy_files_to_db.py \
        -c "sqlite_file:output/scenarios/$SCENARIO/Alignment_SIMCOND.db/SIMCOND" \
        -s "output/scenarios/$SCENARIO/SIMCOND"
}

make_scenario "tip_x=0um_y=-10000um" 0 -10000
make_scenario "tip_x=0um_y=-1000um" 0 -1000
make_scenario "tip_x=0um_y=-500um" 0 -500
make_scenario "tip_x=0um_y=-100um" 0 -100
make_scenario "Nominal" 0 0
make_scenario "tip_x=0um_y=+100um" 0 100
make_scenario "tip_x=0um_y=+500um" 0 500
make_scenario "tip_x=0um_y=+1000um" 0 1000
make_scenario "tip_x=0um_y=+10000um" 0 10000

make_scenario "tip_x=-10000um_y=0um" -10000 0
make_scenario "tip_x=-1000um_y=0um" -1000 0
make_scenario "tip_x=-500um_y=0um" -500 0
make_scenario "tip_x=-100um_y=0um" -100 0
make_scenario "tip_x=+100um_y=0um" 100 0
make_scenario "tip_x=+500um_y=0um" 500 0
make_scenario "tip_x=+1000um_y=0um" 1000 0
make_scenario "tip_x=+10000um_y=0um" 10000 0

make_scenario "tip_x=100um_y=-500um" -500 100
make_scenario "tip_x=100um_y=-100um" -100 100
make_scenario "tip_x=100um_y=+100um" 100 100
make_scenario "tip_x=100um_y=+500um" 500 100

make_scenario "tip_x=-100um_y=-500um" -500 -100
make_scenario "tip_x=-100um_y=-100um" -100 -100
make_scenario "tip_x=-100um_y=+100um" 100 -100
make_scenario "tip_x=-100um_y=+500um" 500 -100

