#!/bin/bash

# check that we have the relevant files (and get them if necessary)

cd graphhopper_data

if test -f "$GRAPHHOPPER_EXECUTABLE"; then
    echo "Using cached graphhopper executable"
else
    echo "Downloading graphhopper executable"
    wget --progress=dot:mega "$GRAPHHOPPER_DOWNLOAD_FOLDEr$GRAPHHOPPER_EXECUTABLE"
fi

if test -f "$MAP_FILE"; then
    echo "Using cached map file"
else
    echo "Downloading map file"
    wget --progress=dot:mega "$MAP_DOWNLOAD_FOLDER$MAP_FILE"
fi

# launches instance of graphhopper routing engine
java -Ddw.graphhopper.datareader.file=$MAP_FILE -jar $GRAPHHOPPER_EXECUTABLE server /config.yml


