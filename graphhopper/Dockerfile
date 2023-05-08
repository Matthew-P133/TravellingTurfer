FROM openjdk:8-jdk

COPY . .
EXPOSE 8989

RUN mkdir -p graphhopper_data
WORKDIR /graphhopper_data

RUN wget https://github.com/graphhopper/graphhopper/releases/download/5.3/graphhopper-web-5.3.jar

# run routing engine, downloading map if necessary
ENTRYPOINT /entrypoint.sh


