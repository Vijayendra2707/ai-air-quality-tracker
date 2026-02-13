var map=L.map('map').setView([19.07,72.87],12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
.addTo(map);

L.polyline([[19.07,72.87],[19.08,72.90]],{color:"blue"}).addTo(map);
L.polyline([[19.07,72.87],[19.09,72.92]],{color:"green"}).addTo(map);
