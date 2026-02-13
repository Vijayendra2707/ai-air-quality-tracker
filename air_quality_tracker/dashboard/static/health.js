function predict(){
fetch("/api/health/?aqi=200&humidity=70&age=60&asthma=1&heart=0")
.then(r=>r.json())
.then(data=>{
document.getElementById("risk").innerText =
"Risk: "+data.risk+" | "+data.recommendation;
});
}
