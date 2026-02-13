navigator.geolocation.getCurrentPosition(function(position) {

    fetch(`/api/aqi/?lat=${position.coords.latitude}&lon=${position.coords.longitude}`)
    .then(res => res.json())
    .then(data => {

        document.getElementById("aqi-value").innerText = data.aqi;

        new Chart(document.getElementById("pollutionChart"), {
            type: "radar",
            data: {
                labels: ["PM2.5","PM10","CO","NO2","O3"],
                datasets: [{
                    label: "Pollution",
                    data: [
                        data.pm25,
                        data.pm10,
                        data.co,
                        data.no2,
                        data.o3
                    ]
                }]
            }
        });

    });

});
