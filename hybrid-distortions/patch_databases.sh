#!/usr/bin/env bash

# Put bash in to strict mode
set -xeuo pipefail

# Define variable we need
BASE_DIR=$PWD
DDDB_TAG="dddb-20160304"
SIMCOND_TAG="sim-20150716-vc-md100"

# Patch DDDB
TMP_DIR=$(mktemp -d)
lb-run LHCb/latest bash -c "dump_db_to_files.py -c sqlite_file:\$SQLITEUPGRADEDBPATH/DDDB.db/DDDB -T $DDDB_TAG -t $(date +"%s000000000") -d $TMP_DIR"
cd $TMP_DIR
patch -p1 < $BASE_DIR/assets/DDDB.patch
cd $BASE_DIR
lb-run LHCb/latest copy_files_to_db.py -c sqlite_file:$BASE_DIR/output/DDDB.db/DDDB -s $TMP_DIR
rm -rf $TMP_DIR

# Patch SIMCOND
TMP_DIR=$(mktemp -d)
lb-run LHCb/latest bash -c "dump_db_to_files.py -c sqlite_file:\$SQLITEUPGRADEDBPATH/SIMCOND.db/SIMCOND -T $SIMCOND_TAG -t $(date +"%s000000000") -d $TMP_DIR"
cd $TMP_DIR
patch -p1 < $BASE_DIR/assets/SIMCOND.patch
cd $BASE_DIR
lb-run LHCb/latest copy_files_to_db.py -c sqlite_file:$BASE_DIR/output/SIMCOND.db/SIMCOND -s $TMP_DIR
rm -rf $TMP_DIR
