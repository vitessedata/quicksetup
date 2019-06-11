#!/bin/bash

source env.sh
source ./deepgreendb/greenplum_path.sh

rm -fr xdrive && pass || fail
mkdir -p xdrive && pass || fail
mkdir -p xdrive/images && pass || fail

rm -f ./xdrive.toml 

echo "
[xdrive]
dir = \"$DIR/xdrive\"
pluginpath = [\"$DIR/xdrive/plugin\"] 
port=31416
host = [ \"localhost\" ]

[[xdrive.mount]]
name = \"images\" 
argv = [\"dgtools/ls_file\", \"$DIR/xdrive/images\"] 
" >> xdrive.toml

xdrctl deploy ./xdrive.toml
xdrctl start ./xdrive.toml

mkdir -p $DIR/xdrive/plugin/dgtools && pass || fail
cp ../xdrive/ls_file $DIR/xdrive/plugin/dgtools/ && pass || fail
tar -C ./xdrive/images -xzf 101_ObjectCategories.tar.gz && pass || fail

mkdir -p ./xdrive/images/search
cp ./xdrive/images/101_ObjectCategories/soccer_ball/image_0001.jpg ./xdrive/images/search/object.jpg


