window.onload = function () {

    

    // display map
    var map = L.map('map').setView([59.3357, 18.07292], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap',
        preferCanvas: true,
    }).addTo(map);

    // contains the zones in the route
    markerGroup = L.layerGroup().addTo(map);
    routeGroup = L.layerGroup().addTo(map);
    var geoJSON;

    // add route to map
    id = parseInt(document.getElementById("id").innerHTML);
    loadRoute(id);
    updateStats(id);

    document.getElementById('downloadRoute').addEventListener('click', downloadRoute);
    document.getElementById('shareRoute').addEventListener('click', copyURL);
    
    // gets route from back end and draws it on the map
    function loadRoute(id) {

        zonePromise = fetch("/generate/", {
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
                drawRoute(data);
            });
    }

    function updateStats(id) {
        fetch("/route-stats/", {
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
                document.getElementById('routeDistance').innerHTML = data.distance;
                document.getElementById('routeZones').innerHTML = data.length;
                document.getElementById('routePointsPerHour').innerHTML = data.points_per_hour;
                document.getElementById('routeTakeoverPoints').innerHTML = data.takeover_points;
            });
    }

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

    // centres the map on centre of route
    function centreMap(data) {

        coordinates = data['coordinates'];

        minLongitude = maxLongitude = coordinates[0][0];
        minLatitude = maxLatitude = coordinates[0][1];

        coordinates.forEach(function(coordinate) {
            long = coordinate[0];
            lat = coordinate[1];
            if (long < minLongitude) {minLongitude = long}
            if (long > maxLongitude) {maxLongitude = long}
            if (lat < minLatitude) {minLatitude = lat}
            if (lat > maxLatitude) {maxLatitude = lat}
        });

        topLeftBound = L.latLng(minLatitude, maxLongitude);
        bottomRightBound = L.latLng(maxLatitude, minLongitude);

        bounds = L.latLngBounds(topLeftBound, bottomRightBound);
        map.fitBounds(bounds)
    }

    style = {
        "color": "#ff7800",
        "weight": 5,
        "opacity": 0.65
    };

    function drawRoute(data) {
        markerGroup.clearLayers();
        routeGroup.clearLayers();
        geoJSON = data.geoJSON
        centreMap(data.geoJSON);
        L.geoJSON(data.geoJSON, {style: style}).addTo(routeGroup);
        drawZones(data.zones);
    }

    function drawZones(data) {
        routeLength = data.length

        data.forEach(function(zone) {
            zoneLatLng = L.latLng((zone.latitude), (zone.longitude));;
            circle_marker = L.circle(zoneLatLng, { 'radius': 30 }).addTo(markerGroup);
            circle_marker.on("click", onCircleClick);
            circle_marker.bindTooltip(zone.position.toString()).openTooltip();
            // attach zone properties to marker
            L.setOptions(circle_marker, zone);
        })
        
    }

    // changes start/end point to clicked zone or reverses direction of route
    function onCircleClick(e) {
        fetch("/update/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({'id': id, 'zone_id': e.target.options.id}),
            credentials: 'same-origin',
        })
            .then(loadRoute(id));
    }


    function downloadRoute() {

        blob = new Blob([togpx(geoJSON)]);
        url = window.URL.createObjectURL(blob);

        a = document.createElement('a');
        document.body.appendChild(a);
        a.style = "display: none";
        a.href = url;
        a.download = 'TravellingTurfer_Route' + id.toString() + ".gpx";
        a.click();

        window.URL.revokeObjectURL(url);

        
    }

    document.getElementById('help').addEventListener('click', toggleInstructions);
    document.getElementById('help-close').addEventListener('click', toggleInstructions);

    function toggleInstructions() {
        elem = document.getElementById('instructions')
        if (elem.className == 'overlay') {
            elem.setAttribute('class', 'overlay-hidden')
        } else {
            elem.setAttribute('class', 'overlay')
        }
    }


    function copyURL() {
        
        url = window.location.toString();
        navigator.clipboard.writeText(url);
        overlay("Route URL copied to clipboard");
      } 

    function overlay(text) {

        newOverlay = document.createElement('div')
        newOverlay.setAttribute('class', 'overlay')

        overlayItem = document.createElement('div')
        overlayItem.setAttribute('class', 'alert')
        
        p = document.createElement('p')
        p.innerHTML = text;
        overlayItem.appendChild(p);

        closeButton = document.createElement('div')
        closeButton.setAttribute('class', 'close-button')
        closeButton.innerHTML = "&#10060;"
        closeButton.addEventListener('click', closeAlert);


        newOverlay.appendChild(overlayItem);
        newOverlay.appendChild(closeButton);
        document.body.appendChild(newOverlay);
    }

    function closeAlert(e) {
        console.log(e.target.parentNode)
        e.target.parentNode.remove();
    }

};




