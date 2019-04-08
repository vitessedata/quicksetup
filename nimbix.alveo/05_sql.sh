#!/bin/bash

source env.sh
source ./deepgreendb/greenplum_path.sh

dg setup -all nimbix
psql -f sql/img.sql nimbix
