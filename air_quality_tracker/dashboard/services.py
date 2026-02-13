import requests
from django.conf import settings
import polyline
import math
def fetch_aqi(city=None, lat=None, lon=None):

    if city:
        url = f"https://api.waqi.info/feed/{city}/"
    elif lat and lon:
        url = f"https://api.waqi.info/feed/geo:{lat};{lon}/"
    else:
        return None

    params = {"token": settings.AQICN_API_TOKEN}

    r = requests.get(url, params=params)

    if r.status_code != 200:
        return None

    data = r.json()

    if data["status"] != "ok":
        return None

    aqi_data = data["data"]

    # 🔥 Extract station coordinates (IMPORTANT for heatmap)
    geo = aqi_data.get("city", {}).get("geo", [None, None])
    latitude = geo[0]
    longitude = geo[1]

    aqi_value = aqi_data.get("aqi")

    return {
        "aqi": aqi_value,
        "category": get_category(aqi_value),
        "lat": latitude,
        "lon": longitude,
        "humidity": aqi_data.get("iaqi", {}).get("h", {}).get("v"),
        "pm25": aqi_data.get("iaqi", {}).get("pm25", {}).get("v"),
        "pm10": aqi_data.get("iaqi", {}).get("pm10", {}).get("v"),
        "no2": aqi_data.get("iaqi", {}).get("no2", {}).get("v"),
        "o3": aqi_data.get("iaqi", {}).get("o3", {}).get("v"),
        "co": aqi_data.get("iaqi", {}).get("co", {}).get("v"),
    }

def get_category(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"



def fetch_routes(start_lat, start_lon, end_lat, end_lon):

    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": settings.ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            [float(start_lon), float(start_lat)],
            [float(end_lon), float(end_lat)]
        ],
        "alternative_routes": {
            "target_count": 2,
            "weight_factor": 1.6
        }
    }

    response = requests.post(url, json=body, headers=headers)

    if response.status_code != 200:
        return None

    return response.json()

def extract_route_points(route_data):
    routes = route_data["routes"]
    extracted_routes = []

    for route in routes:
        geometry = route["geometry"]
        coords = polyline.decode(geometry)

        duration = route["summary"]["duration"]  # seconds
        distance = route["summary"]["distance"]  # meters

        extracted_routes.append({
            "coordinates": coords,
            "duration": duration,
            "distance": distance
        })

    return extracted_routes

def calculate_route_aqi(route_points):

    sampled_points = route_points[::10]  # every 10th coordinate
    total_aqi = 0
    count = 0

    for lat, lon in sampled_points:
        aqi_data = fetch_aqi(lat=lat, lon=lon)

        if aqi_data and aqi_data["aqi"]:
            total_aqi += aqi_data["aqi"]
            count += 1

    if count == 0:
        return None

    return total_aqi / count

def calculate_exposure(avg_aqi, duration_seconds):

    hours = duration_seconds / 3600
    return avg_aqi * hours


# ---------- Distance calculator ----------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)

    a = math.sin(dLat/2)**2 + \
        math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * \
        math.sin(dLon/2)**2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


# ---------- Smart Route Analyzer ----------
def analyze_routes(start_lat, start_lon, end_lat, end_lon):

    try:
        start_lat = float(start_lat)
        start_lon = float(start_lon)
        end_lat = float(end_lat)
        end_lon = float(end_lon)
    except ValueError:
        return None

    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": settings.ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            [start_lon, start_lat],
            [end_lon, end_lat]
        ],
        "instructions": False,
        "alternative_routes": {
            "target_count": 2
        }
    }

    try:
        response = requests.post(url, json=body, headers=headers, timeout=6)
    except requests.exceptions.RequestException:
        return None

    if response.status_code != 200:
        return None

    data = response.json()

    fastest_route = None
    cleanest_route = None

    lowest_time = float("inf")
    lowest_exposure = float("inf")

    for route in data["routes"]:

        duration_sec = route["summary"]["duration"]
        duration_min = round(duration_sec / 60, 2)

        geometry = route["geometry"]
        decoded = polyline.decode(geometry)

        coordinates = [[lat, lon] for lat, lon in decoded]

        # ---------- Calculate AQI exposure ----------
        total_exposure = 0
        total_distance = 0

        # Sample every 8th point (balance speed + accuracy)
        step = max(1, len(coordinates) // 8)

        for i in range(0, len(coordinates) - 1, step):

            lat1, lon1 = coordinates[i]
            lat2, lon2 = coordinates[i + 1]

            distance = haversine(lat1, lon1, lat2, lon2)

            zone = fetch_aqi(lat=lat1, lon=lon1)

            if zone and zone["aqi"]:
                total_exposure += zone["aqi"] * distance
                total_distance += distance

        avg_aqi = total_exposure / total_distance if total_distance else 500

        # ---------- Fastest route ----------
        if duration_min < lowest_time:
            lowest_time = duration_min
            fastest_route = {
                "coordinates": coordinates,
                "duration": duration_min
            }

        # ---------- Cleanest route ----------
        if avg_aqi < lowest_exposure:
            lowest_exposure = avg_aqi
            cleanest_route = {
                "coordinates": coordinates,
                "avg_aqi": round(avg_aqi, 2)
            }
    print("Number of routes:", len(data["routes"]))
    return {
        "fastest": fastest_route,
        "cleanest": cleanest_route
    }