window.onload = function() {

    // display map centred on sweden when page is fully loaded
    var map = L.map('map').setView([59.3357, 18.07292], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap',
        preferCanvas: true,
    }).addTo(map);


    markerGroup = L.layerGroup().addTo(map);
    selectedMarkerGroup = L.layerGroup().addTo(map);


    // defines action to take when a zone marker is clicked
    function onCircleClick(e) {
        // select marker
         if (markerGroup.hasLayer(e.target)) { 
            e.target.setStyle({color: '#ff0000'});
            markerGroup.removeLayer(e.target);
            selectedMarkerGroup.addLayer(e.target);
        } else { // deselect marker
            e.target.setStyle({color: '#3388ff'});
            selectedMarkerGroup.removeLayer(e.target);
            markerGroup.addLayer(e.target);
        }

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

        zonePromise = fetch("zones", {
            method: 'POST', 
            headers: {'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')},
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

    function updateStats() {
        selectedZones = 0;
        selectedMarkerGroup.eachLayer(function() {selectedZones++});
        document.getElementById("selectedZoneStats").innerHTML = selectedZones;

    }


    // display zones on the map
    function drawZones(zoneArray) {

        // clear all (unselected) zones before drawing new ones (avoids slowdown associated with displaying lots of zones)
        markerGroup.clearLayers();

        // put each zone on map (if not already present as a selected zone) and attach event listener to each
        zoneArray.forEach(zone => {

            zoneLatLng = L.latLng((zone.latitude), (zone.longitude));
            zonePresent = false;

            selectedMarkerGroup.eachLayer(function(layer) {
                if (layer instanceof L.Circle) {
                    if (layer.getLatLng().equals(zoneLatLng)) {
                        zonePresent = true;
                    }
                }
            });
            
            if (!zonePresent) {
                circle_marker = L.circle(zoneLatLng, {'radius': 30}).addTo(markerGroup);
                circle_marker.on("click", onCircleClick);
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
};


