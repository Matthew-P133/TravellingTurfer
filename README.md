# TravellingTurfer

Route optimisation tool for geo-location based game, Turf. At the time of writing, the app is available at https://travellingturfer.fun/map/

Built as a project for the MSc in Software Development at the University of Glasgow.

## Usage

The easiest way to deploy the application locally is with Docker and Docker Compose. These instructions are written and tested for Linux (but should also work in Windows with Docker-desktop and Windows Subsystem for Linux).

Clone (or download) this repository, making sure that the top-level directory (the one containing docker-compose.yml) is called 'TravellingTurfer'.

To run the project with default settings, navigate to the top-level project directory and run:

```
cp sample.env .env
docker-compose up --build
```

This will build and spin up the various containers. Note that the first build can take a few minutes (due to building docker images, downloading the GraphHopper executable and map data, GraphHopper parsing map data into RAM, and populating the database).

Once everything is up you can access the application on: http://127.0.0.1:10000/

And to spin down:

```
docker-compose down
```

The containers for GraphHopper and the Django Application keep persistent data in bind mounts, stored in the top level directory under volumes.

This makes future spin ups much faster because the map data does not need to be redownloaded and re-parsed by graphhopper.

Have a look a the environment variables in .env (particularly PURGE_DB and POPULATE_DB) for future spin ups.

## Making changes

Code changes:

1. Make desired changes to code files
2. Spin down the containers (if applicable):
```
docker-compose down
```
3. Spin the containers back up (the --build flag ensures the docker images are rebuilt with the new code):
```
docker-compose up --build
```

Config changes (e.g. changing the map used):

1. Find a url for the desired map file (in .pbf format) such as https://download.geofabrik.de/europe/germany/hamburg-latest.osm.pbf
2. Edit .env:
```
...
MAP_FILE=hamburg-latest.osm.pbf
MAP_DOWNLOAD_FOLDER=https://download.geofabrik.de/europe/germany/
...
```
3. Spin down and up the containers:
```
docker-compose down && docker-compose up --build
```

## Project structure

Travelling Turfer deployments are made up of three containers:

1. tt_web - the main Travelling Turfer (Django) web application. This is responsible for applying route optimisation algorithms to route optimisation jobs, as well as orchestrating application flow: receiving and servicing requests from the frontend (custom CSS/HTML/JavaScript, built around leaflet); accessing the SQLite3 database (e.g., to store and retrieve routes); and obtaining real-world A-B distances between pairs of zones for use in distance matrices in route optimisation jobs from routing engine, GraphHopper.
2. tt_graphhopper - the routing engine which Travelling Turfer uses for raw A->B distances for distance matrix generation.
3. tt_nginx - a reverse web proxy which serves the application

## Project layout

nginx/ and graphhopper/ contain Dockerfiles and scripts for spinning up these dependencies

web/ contains the main travelling turfer web application and the Dockerfile for building it into a docker image

volumes/ contains bind mounts for persistent container data (such as map files and the database)

Within web/:

/TravellingTurfer/ contains Django settings and configuration.

Application logic including the route optimisation algorithms, and unit and integration tests can be found in /routing/.

Frontend code is in /static/.

/reference_TSP_solutions/ contains route optimisation tasks with know optimal solutions - these can be used to benchmark route optimisation algorithms using benchmark.py.

populate_zones.py is used for populating the database when the app is deployed for the first time.

requirements.txt contains a list of python dependencies

At the top level:

docker-compose.yml orchestrates application deployment.
sample.env contains default contents for the .env file containing environment variables needed to deploy the app.
