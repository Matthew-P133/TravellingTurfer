# TravellingTurfer

Route optimisation tool for geo-location based game, Turf. At the time of writing, the app is available at https://travellingturfer.fun/map/

Built as a project for the MSc in Software Development at the University of Glasgow.

## Project structure

At the core of TravellingTurfer is a Django application. This is responsible for applying route optimisation algorithms to route optimisation jobs, as well as orchestrating application flow: rceiving and servicing requests from the frontend (custom CSS/HTML/JavaScript, built around leaflet); accessing the SQLite3 database (e.g., to store and retrieve routes); and obtaining real-world A-B distances between pairs of zones for use in distance matrices in route optimisation jobs from routing engine, GraphHopper.

## Project layout

/TravellingTurfer/ contains Django settings and configuration.

Application logic including the route optimisation algorithms, and unit and integration tests can be found in /routing/.

Frontend code is in /static/.

/reference_TSP_solutions/ contains route optimisation tasks with know optimal solutions - these can be used to benchmark route optimisation algorithms using benchmark.py.

/nginx/ and /graphhopper/ contain Dockerfiles and scripts for spinning up these dependencies.

/db/ is an empty folder which the database goes in.

Dockerfile, docker-compose.yml and launch.sh in the top level directory are used for deploying the app.

populate_zones.py is used for populating the database when the app is deployed for the first time.

requirements.txt contains a list of python dependencies.

sample.env contains default contents for the .env file containing environment variables needed to run the app.

## Usage

The easiest way to deploy the application locally is with Docker and Docker Compose. To install these in linux run:

```
apt install docker
apt install docker-compose
```

Next download or clone this repository.

In a terminal window in the top project directory:

```
mv sample.env .env
docker-compose -f docker-compose.yml up
```

This will build and spin up the various containers. Note that it can take a while on the first build (due to building docker images, downloading the GraphHopper executable and map data, GraphHopper parsing map data into RAM, and populating the database).

You can check progress once the images have been built with:

```
docker-compose -f docker-compose.yml -f logs.
```

Once everything is up you can access the application on: http://127.0.0.1:1337/

And to spin down:

```
docker-compose -f docker-compose.yml down
```

The containers for GraphHopper and the Django Application have persistent volumes associated with them (to speed up GraphHopper spin up, and persist the database). To get rid of these too on spin down, run:

```
docker-compose -f docker-compose.yml down -v
```

Future spin ups are much faster (~5 seconds).

Have a look a the environment variables in .env (particularly PURGE_DB and POPULATE_DB) for future spin ups.
