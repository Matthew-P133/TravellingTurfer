window.onload = function() {

    // display map centred on sweden when page is fully loaded
    var map = L.map('map').setView([59.3357, 18.07292], 11);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    }).addTo(map);

};


