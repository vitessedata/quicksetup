#!/bin/bash

source env.sh
source ./deepgreendb/greenplum_path.sh

dg setup -all $USER 
psql -f ../sql/img.sql $USER
