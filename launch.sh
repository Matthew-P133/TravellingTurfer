#!/bin/bash

# if no database, create an empty one
cd /code/db
if test -f "db.sqlite3"; then
    echo "Found existing database"

    if [ $PURGE_DB -eq 1 ]; then

        echo "Purging database"
        # rename old database
        name=db.sqlite3.old
        if [ -e $name ]; then
            i=0
            while [ -e $name-$i ]; do
                let i++
            done
            name=$name-$i
        fi
        mv db.sqlite3 $name
    
        # create new one
        echo "Creating a new database"
        touch db.sqlite3  
    fi

else
    echo "No database found, setting one up"
    touch db.sqlite3
fi

# apply any migrations
cd /code
python manage.py makemigrations
python manage.py migrate

if [ $UPDATE_ZONES -eq 1 ]; then
    cd /code
    echo "Updating zones in database"
    python populate_zones.py
fi

# collect static files and run the server
cd /code
python manage.py collectstatic
gunicorn TravellingTurfer.wsgi:application --bind 0.0.0.0:8000