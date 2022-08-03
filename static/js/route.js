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
        latitudeSum = 0;
        longitudeSum = 0;

        coordinates.forEach(element => {
            latitudeSum += element[1];
            longitudeSum += element[0];
        });

        centre = [latitudeSum/coordinates.length, longitudeSum/coordinates.length]

        // TODO - set zoom intelligently so that route just all visible
        zoomLevel = 16

        map.setView(centre, zoomLevel)
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
};




