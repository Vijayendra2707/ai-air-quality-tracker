function getAQI(){
let city=document.getElementById("city").value;

fetch(`/api/aqi/?city=${city}`)
.then(r=>r.json())
.then(data=>{

const labels=["PM2.5","PM10","CO","NO2","O3"];

new Chart(document.getElementById("radar"),{
type:"radar",
data:{labels:labels,datasets:[{data:[
data.pm25,data.pm10,data.co,data.no2,data.o3]}]}
});

const category=["Good","Fair","Moderate","Poor","Very Poor"];
document.getElementById("category").innerText=
"AQI: "+category[data.aqi-1];

});
}

fetch("/api/history/")
.then(r=>r.json())
.then(data=>{
new Chart(document.getElementById("line"),{
type:"line",
data:{labels:data.history.map((_,i)=>i),
datasets:[{label:"History",data:data.history}]}
});
});

var map=L.map('map').setView([19.07,72.87],10);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
.addTo(map);

fetch("/api/history/")
.then(r=>r.json())
.then(data=>{
L.heatLayer(
data.history.map((v,i)=>[19.07+i*0.01,72.87+i*0.01,v]),
{radius:25}
).addTo(map);
});
