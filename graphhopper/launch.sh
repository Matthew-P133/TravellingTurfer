#!/bin/bash

# check that we have the relevant files (and get them if necessary)

cd graphhopper_data

if test -f "$graphhopper_executable"; then
    echo "Using cached graphhopper executable"
else
    echo "Downloading graphhopper executable"
    wget --progress=dot:mega "$graphhopper_download_folder$graphhopper_executable"
fi

if test -f "$map_file"; then
    echo "Using cached map file"
else
    echo "Downloading map file"
    wget --progress=dot:mega "$map_download_folder$map_file"
fi

# launches instance of graphhopper routing engine
java -Ddw.graphhopper.datareader.file=$map_file -jar $graphhopper_executable server /config.yml
