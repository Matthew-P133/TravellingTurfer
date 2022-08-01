window.onload = function () {

    // display map when page is fully loaded
    var map = L.map('map').setView([56, -4], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap',
        preferCanvas: true,
    }).addTo(map);

    markerGroup = L.layerGroup().addTo(map);
    selectedMarkerGroup = L.layerGroup().addTo(map);

    map.whenReady(onMapMoveEnd);


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

            document.getElementById("prompt").innerHTML = "";
            map.hasLayer(markerGroup) ? {} : map.addLayer(markerGroup);
            map.hasLayer(selectedMarkerGroup) ? {} : map.addLayer(selectedMarkerGroup);
        } else {
            // zoomed out too far
            document.getElementById("prompt").innerHTML = "Zoom in to see zones"
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
            .then(data => drawZones(data));
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


    // attach event functions to event listeners
    map.on("moveend", onMapMoveEnd);
    


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
        .then(response => window.location.replace("http://127.0.0.1:8000/route" + response + "/"));

    }

    document.getElementById('selectVisible').addEventListener('click', selectVisible);
    document.getElementById('deselectVisible').addEventListener('click', deselectVisible);
    document.getElementById('deselectAll').addEventListener('click', deselectAll);

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


};




