fetch("/api/indoor/")
.then(r=>r.json())
.then(data=>{
new Chart(document.getElementById("indoorChart"),{
type:"bar",
data:{
labels:["Indoor","Outdoor"],
datasets:[{data:[data.indoor,data.outdoor]}]
}
});
});
