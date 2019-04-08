#!/bin/bash

source env.sh
source ./deepgreendb/greenplum_path.sh

rm -fr data && pass || fail
mkdir -p data && pass || fail
rm -fr monagent && pass || fail
mkdir -p monagent && pass || fail

gpinitsystem -c cluster.conf --lc-collate=C
createdb nimbix 
