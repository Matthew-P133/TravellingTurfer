window.onload = function() {

    // display map centred on sweden when page is fully loaded
    var map = L.map('map').setView([59.3357, 18.07292], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap',
        preferCanvas: true,
    }).addTo(map);


    markerGroup = L.layerGroup().addTo(map);


    // defines action to take when a zone marker is clicked
    function onCircleClick(e) {
        alert("TODO: display zone stats for zone with lat/lng: " + e.latlng);
    }


    // when map moves (on pan or zoom) get and display zones
    function onMapMoveEnd(e) {
        //markerGroup.clearLayers();
        if (map.getZoom() >= 11) {
            document.getElementById("prompt").innerHTML = "";
            getZones(map.getBounds().getNorthEast(), map.getBounds().getSouthWest());
        } else {
            document.getElementById("prompt").innerHTML = "Zoom in to see zones"
        }
    }


    // query Turf API for zones within specified bounds
    function getZones(northEast, southWest) {

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


    // display zones on the map
    function drawZones(zoneArray) {
        zoneArray.forEach(zone => {

            zoneLatLng = L.latLng((zone.latitude), (zone.longitude));
            circle_marker = L.circleMarker(zoneLatLng, {'radius': 2}).addTo(markerGroup);
            circle_marker.on("click", onCircleClick);
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


