from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import AQIHistory, RouteHistory
from .services import fetch_aqi , analyze_routes
from .ml.forecast import forecast
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .ml.health import predict_health
from .ml.anomaly import detect
from django.contrib.auth.decorators import login_required
import random

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})

# ---------- PAGES ----------
@login_required
def dashboard(request):
    return render(request, "index.html")
def health_page(request):
    return render(request, "health.html")

def route_page(request):
    return render(request, "route.html")

def indoor_page(request):
    return render(request, "indoor.html")


# ---------- AQI API (CITY BASED USING AQICN) ----------

def aqi_api(request):
    city = request.GET.get("city")

    if not city:
        return JsonResponse({"error": "City required"}, status=400)

    aqi_data = fetch_aqi(city=city)

    if not aqi_data:
        return JsonResponse({"error": "AQI fetch failed"}, status=500)

    AQIHistory.objects.create(
        city=city,
        lat=None,
        lon=None,
        aqi=aqi_data["aqi"]
    )

    return JsonResponse(aqi_data)


# ---------- CURRENT AQI (LAT/LON BASED USING AQICN) ----------

def current_aqi_api(request):
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")

    if not lat or not lon:
        return JsonResponse({"error": "Location required"}, status=400)

    aqi_data = fetch_aqi(lat=lat, lon=lon)

    if not aqi_data:
        return JsonResponse({"error": "AQI fetch failed"}, status=500)

    return JsonResponse(aqi_data)


# ---------- HISTORY + FORECAST + ANOMALY ----------

def history_api(request):
    history = list(
        AQIHistory.objects.values_list("aqi", flat=True)
        .order_by("-timestamp")[:30]
    )

    history.reverse()
    history = [int(x) for x in history]

    forecast_value = int(forecast(history)) if history else 0
    anomalies_raw = detect(history)
    anomalies = [int(x) for x in list(anomalies_raw)] if anomalies_raw is not None else []

    return JsonResponse({
        "history": history,
        "forecast": forecast_value,
        "anomaly": anomalies
    })

def heatmap_api(request):
    city = request.GET.get("city")

    if not city:
        return JsonResponse({"error": "City required"}, status=400)

    # Get center coordinates
    from .services import fetch_aqi

    center_data = fetch_aqi(city=city)

    if not center_data or "lat" not in center_data:
        return JsonResponse({"error": "City not found"}, status=400)

    center_lat = float(center_data["lat"])
    center_lon = float(center_data["lon"])

    grid_points = []

    # Create 3x3 grid around city
    offsets = [-0.08, -0.04, 0, 0.04, 0.08]

    for lat_offset in offsets:
        for lon_offset in offsets:
            lat = center_lat + lat_offset
            lon = center_lon + lon_offset

            zone_data = fetch_aqi(lat=lat, lon=lon)

            if zone_data:
                grid_points.append({
                    "lat": lat,
                    "lon": lon,
                    "aqi": zone_data["aqi"]
                })

    return JsonResponse({
        "center_lat": center_lat,
        "center_lon": center_lon,
        "zones": grid_points
    })


# ---------- HEALTH PREDICTION ----------

def health_api(request):
    data = [
        float(request.GET["aqi"]),
        float(request.GET["humidity"]),
        int(request.GET["age"]),
        int(request.GET["asthma"]),
        int(request.GET["heart"])
    ]

    risk = predict_health(data)

    recommendation = "Avoid outdoor activity" if risk == "Severe" else "Safe"

    return JsonResponse({
        "risk": risk,
        "recommendation": recommendation
    })


# ---------- ROUTE OPTIMIZER ----------

def route_api(request):
    aqi = int(request.GET.get("aqi", 100))

    fastest_time = 20
    clean_time = 30

    fastest_exposure = fastest_time * aqi
    clean_exposure = clean_time * (aqi - 1)

    RouteHistory.objects.create(
        source="A",
        destination="B",
        fastest_exposure=fastest_exposure,
        cleanest_exposure=clean_exposure
    )

    return JsonResponse({
        "fastest": fastest_exposure,
        "cleanest": clean_exposure
    })


# ---------- INDOOR VS OUTDOOR ----------

def indoor_api(request):
    indoor = random.randint(20, 150)
    outdoor = 100

    suggestion = "Ventilate room" if indoor > outdoor else "Safe"

    return JsonResponse({
        "indoor": indoor,
        "outdoor": outdoor,
        "suggestion": suggestion
    })


# ---------- COMPARE CITIES ----------

def compare_page(request):
    return render(request, "compare.html")

def compare_api(request):
    city = request.GET.get("city")
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")

    if not city or not lat or not lon:
        return JsonResponse({"error": "Missing data"}, status=400)

    # Current location AQI
    current_data = fetch_aqi(lat=lat, lon=lon)

    # Selected city AQI
    city_data = fetch_aqi(city=city)

    if not current_data or not city_data:
        return JsonResponse({"error": "AQI fetch failed"}, status=500)

    return JsonResponse({
        "current_aqi": current_data["aqi"],
        "city_aqi": city_data["aqi"],
        "current_category": current_data["category"],
        "city_category": city_data["category"]
    })
def smart_route_api(request):

    start_lat = request.GET.get("start_lat")
    start_lon = request.GET.get("start_lon")
    end_lat = request.GET.get("end_lat")
    end_lon = request.GET.get("end_lon")

    if not all([start_lat, start_lon, end_lat, end_lon]):
        return JsonResponse({"error": "Missing parameters"}, status=400)

    result = analyze_routes(start_lat, start_lon, end_lat, end_lon)

    if not result:
        return JsonResponse({"error": "Route analysis failed"}, status=500)

    return JsonResponse(result)
