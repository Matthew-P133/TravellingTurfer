window.onload = function () {

    // display map
    var map = L.map('map').setView([59.3357, 18.07292], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap',
        preferCanvas: true,
    }).addTo(map);

    // add route to map
    id = document.getElementById('id').innerHTML;
    loadRoute(id);

    
    // gets route from back end and draws it on the map
    function loadRoute(id) {

        zonePromise = fetch("/generate/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                'id':id
            }),
            credentials: 'same-origin',
        })
            .then(response => response.json())
            .then(data => drawRoute(data));
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
        centreMap(data);
        L.geoJSON(data, {style: style}).addTo(map);
    }
};




