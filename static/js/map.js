window.onload = function () {

    // display map when page is fully loaded
    var map = L.map('map').setView([56, -4], 11);
    normalMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap',
        preferCanvas: true,
    });

    satelliteMap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19,
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
        preferCanvas: true,
    });

    normalMap.addTo(map);


    markerGroup = L.layerGroup().addTo(map);
    selectedMarkerGroup = L.layerGroup().addTo(map);

    onMapMoveEnd();




    // defines action to take when a zone marker is clicked
    function onCircleClick(e) {
        // select marker
        if (markerGroup.hasLayer(e.target)) {
            e.target.setStyle({ color: '#ff0000' });
            markerGroup.removeLayer(e.target);
            selectedMarkerGroup.addLayer(e.target);
        } else { // deselect marker
            e.target.setStyle({ color: '#3388ff' });
            selectedMarkerGroup.removeLayer(e.target);
            markerGroup.addLayer(e.target);
        }
        // keep display of selected zone statistics up to date
        updateStats();
    }


    // when map moves (on pan or zoom) get and display zones
    function onMapMoveEnd(e) {

        if (map.getZoom() >= 11) {

            updateZones(map.getBounds().getNorthEast(), map.getBounds().getSouthWest());
            map.hasLayer(markerGroup) ? {} : map.addLayer(markerGroup);
            map.hasLayer(selectedMarkerGroup) ? {} : map.addLayer(selectedMarkerGroup);
        } else {
            // zoomed out too far
            map.removeLayer(markerGroup);
            map.removeLayer(selectedMarkerGroup);
        }
    }


    // query Turf API for zones within specified bounds
    function updateZones(northEast, southWest) {

        zonePromise = fetch("/zones/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                'northEastLat': northEast.lat,
                'northEastLong': northEast.lng,
                'southWestLat': southWest.lat,
                'southWestLong': southWest.lng
            }),
            credentials: 'same-origin',
        })
            .then(response => response.json())
            .then(data => drawZones(data))
    }


    // calculates and updates aggregate statistics for selected zones
    function updateStats() {
        selectedZones = 0;
        takeoverPoints = 0;
        pointsPerHour = 0;

        selectedMarkerGroup.eachLayer(function (zone) {
            selectedZones++;
            takeoverPoints += zone.options.takeover_points;
            pointsPerHour += zone.options.points_per_hour;
        });
        document.getElementById("selectedZoneCount").innerHTML = selectedZones;
        document.getElementById("selectedZoneTakeoverPoints").innerHTML = takeoverPoints;
        document.getElementById("selectedZonePointsPerHour").innerHTML = pointsPerHour;
    }


    // display zones on the map
    function drawZones(zoneArray) {


        // clear all (unselected) zones before drawing new ones (avoids slowdown associated with displaying lots of zones)
        markerGroup.clearLayers();

        if (!zoneArray[0]['error']) {

            // put each zone on map (if not already present as a selected zone) and attach event listener to each
            zoneArray.forEach(zone => {

                zoneLatLng = L.latLng((zone.latitude), (zone.longitude));
                zonePresent = false;

                selectedMarkerGroup.eachLayer(function (layer) {
                    if (layer instanceof L.Circle) {
                        if (layer.getLatLng().equals(zoneLatLng)) {
                            zonePresent = true;
                        }
                    }
                });

                if (!zonePresent) {
                    circle_marker = L.circle(zoneLatLng, { 'radius': 30 }).addTo(markerGroup);
                    circle_marker.on("click", onCircleClick);

                    // attach zone properties to marker
                    L.setOptions(circle_marker, zone);
                }
            });
        }
    }


    // attach event functions to event listeners
    map.on("moveend", onMapMoveEnd);
    map.on("resize", onMapMoveEnd);
    


    // returns value of the cookie with a given name, or null if the cookie is undefined
    function getCookie(name) {
        cookieValue = null;
        if (document.cookie && document.cookie != '') {
            cookies = document.cookie.split(';');
            for (i = 0; i < cookies.length; i++) {
                cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + '=') {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                }
            }
        }
        return cookieValue
    }

    document.getElementById('createRoute').addEventListener('click', createRoute);
    document.getElementById('toggleMap').addEventListener('click', toggleMap)

    function createRoute() {

        // post IDs of zones to be routed to back end
        var payload = [];
        selectedMarkerGroup.eachLayer(marker => payload.push(marker.options.id))


        // make request to back_end optimisation engine - when ready redirect to route page
        fetch("/optimise/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload),
            credentials: 'same-origin',
        }).then(response => response.text())
        .then(function(response) {
            document.getElementById('loader').setAttribute('class', 'loader');
            document.getElementById('id').innerHTML = response;
            showLoading(response);
        })
        
        

    }

    function showLoading(id) {

        function update() {
                fetch("/status/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify([id]),
                credentials: 'same-origin',
            })
            .then(response => response.json())
            .then(function(data) {
                if (!data.status) {
                    updateLoadingBar(data);
                } else {
                    updateLoadingBar(data);
                    clearInterval(repeatJob);
                    
                }
            })
        }
        repeatJob = setInterval(update, 1000);
    }

    document.getElementById('selectVisible').addEventListener('click', selectVisible);
    document.getElementById('deselectVisible').addEventListener('click', deselectVisible);
    document.getElementById('deselectAll').addEventListener('click', deselectAll);

    document.getElementById('goToRoute').addEventListener('click', goToRoute);

    document.getElementById('help').addEventListener('click', toggleInstructions);
    document.getElementById('help-close').addEventListener('click', toggleInstructions);

    function toggleInstructions() {
        elem = document.getElementById('instructions')
        if (elem.className == 'instructions') {
            elem.setAttribute('class', 'instructions-hidden')
        } else {
            elem.setAttribute('class', 'instructions')
        }
    }


    function goToRoute() {
        window.location.replace("../route" + document.getElementById('id').innerHTML + "/")
    }

    function selectVisible() {
        // select all visible unselected markers
        markerGroup.eachLayer(function (layer) {
            layer.setStyle({ color: '#ff0000' });
            markerGroup.removeLayer(layer);
            selectedMarkerGroup.addLayer(layer);
        });
            updateStats();
    };

    function deselectVisible() {
        // deselect visible selected markers
        selectedMarkerGroup.eachLayer(function (layer) {
            if (map.getBounds().contains(layer.getLatLng())) {
                layer.setStyle({ color: '#3388ff' });
                selectedMarkerGroup.removeLayer(layer);
                markerGroup.addLayer(layer);
            }
        });
            updateStats();
    };


    function deselectAll() {
        // deselect visible selected markers
        selectedMarkerGroup.eachLayer(function (layer) {
            layer.setStyle({ color: '#3388ff' });
            selectedMarkerGroup.removeLayer(layer);
            markerGroup.addLayer(layer);
        });
            updateStats();
    };

    function toggleMap() {
        if (map.hasLayer(normalMap)) {
            map.removeLayer(normalMap)
            satelliteMap.addTo(map);
        }
         else if (map.hasLayer(satelliteMap)) {
            map.removeLayer(satelliteMap)
            normalMap.addTo(map);
        }
    }

    function updateLoadingBar(data) {
       
            elem = document.getElementById("loader-distance-matrix-message")
            if (data.distance_matrix_generation_ms == -1) {
                elem.innerHTML = data.message;
                elem.parentElement.setAttribute("class", 'loader-info')
            } else {
                elem.nextSibling.innerHTML = "&#x2705;"
                elem.innerHTML = `Generated distance matrix  in ${data.distance_matrix_generation_ms.toPrecision(3)} s`;
                elem.parentElement.setAttribute("class", 'loader-info')

                elem = document.getElementById("loader-base-algorithm-message")
                if (data.base_algorithm_ms == -1) {
                    elem.innerHTML = `Performing ${data.method} algorithm`;
                    elem.parentElement.setAttribute("class", 'loader-info')
                } else {
                    elem.nextSibling.innerHTML = "&#x2705;"
                    elem.innerHTML = `${data.method}: found ${data.base_distance.toPrecision(3)} km route in ${data.base_algorithm_ms.toPrecision(3)} s`;
                    elem.parentElement.setAttribute("class", 'loader-info')


                    if (data.two_opt) {
                        elem = document.getElementById("loader-two-opt-message")
                        if (data.two_opt_ms == -1) {
                            elem.innerHTML = `Optimising route with two-opt`;
                            elem.parentElement.setAttribute("class", 'loader-info')
                        }
                        else {
                            elem.nextSibling.innerHTML = "&#x2705;"
                            elem.innerHTML = `Two-opt: shortened by ${data.two_opt_improvement.toPrecision(3)} km in ${data.two_opt_ms.toPrecision(3)} s`;
                            elem.parentElement.setAttribute("class", 'loader-info')
                            
                            if (data.three_opt) {
                                elem = document.getElementById("loader-three-opt-message")
                                if (data.three_opt_ms == -1) {
                                    elem.innerHTML = `Optimising route with three-opt`;
                                    elem.parentElement.setAttribute("class", 'loader-info')
                                }
                                else {
                                    elem.nextSibling.innerHTML = "&#x2705;"
                                    elem.innerHTML = `Three-opt: shortened by ${data.three_opt_improvement.toPrecision(3)} km in ${data.three_opt_ms.toPrecision(3)} s`;
                                    elem.parentElement.setAttribute("class", 'loader-info');
                                }
                            }
                        } 
                    }
                }

                if (data.status) {
                    elem = document.getElementById("loader-status-message")
                    elem.nextSibling.innerHTML = "&#x2705;"
                    elem.innerHTML = "Processed";
                    
                    elem = document.getElementById('goToRoute').parentElement.setAttribute('class', 'loader-info');
                }
            }
        }
};
