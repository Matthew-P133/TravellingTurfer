FROM openjdk:8-jdk

RUN mkdir -p /graphhopper_data
WORKDIR /graphhopper_data
COPY . .
EXPOSE 8989

# run routing engine, downloading files as necessary
CMD ./launch


