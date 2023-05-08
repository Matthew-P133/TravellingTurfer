FROM openjdk:8-jdk

COPY . .
EXPOSE 8989

RUN mkdir -p graphhopper_data

# run routing engine, downloading files as necessary
ENTRYPOINT ./entrypoint.sh


