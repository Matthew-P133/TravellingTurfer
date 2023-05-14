#!/bin/bash

cd /graphhopper_data

# check that we have the map (and get it if necessary)
if test -f "$MAP_FILE"; then
    echo "Using cached map file"
else
    echo "Downloading map file"
    wget --progress=dot:mega "$MAP_DOWNLOAD_FOLDER$MAP_FILE"
fi

# launches instance of graphhopper routing engine
java -Ddw.graphhopper.datareader.file=$MAP_FILE -jar /graphhopper-web-5.3.jar server /config.yml


