#!/usr/bin/env bash

# Put bash in to strict mode
set -xeuo pipefail

function make_scenario {
    SCENARIO=$1
    Z_DIST=$2

    ./assets/build_alignment.py \
        --global-fn=output/scenarios/$SCENARIO/SIMCOND/Conditions/VP/Alignment/Global.xml \
        --modules-fn=output/scenarios/$SCENARIO/SIMCOND/Conditions/VP/Alignment/Modules.xml

    lb-run LHCb/latest copy_files_to_db.py \
        -c sqlite_file:output/scenarios/$SCENARIO/Alignment_SIMCOND.db/SIMCOND \
        -s output/scenarios/$SCENARIO/SIMCOND
}

make_scenario "tip_-100um" -100
make_scenario "tip_-1000um" -1000
make_scenario "Nominal" 0
make_scenario "tip_+100um" 100
make_scenario "tip_+1000um" 1000
