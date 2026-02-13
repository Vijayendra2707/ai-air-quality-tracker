import requests
from django.conf import settings
import polyline
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

def analyze_routes(start_lat, start_lon, end_lat, end_lon):

    route_data = fetch_routes(start_lat, start_lon, end_lat, end_lon)

    if not route_data:
        return None

    routes = extract_route_points(route_data)

    analyzed = []

    for route in routes:
        avg_aqi = calculate_route_aqi(route["coordinates"])

        if avg_aqi is None:
            continue

        exposure = calculate_exposure(avg_aqi, route["duration"])

        analyzed.append({
            "avg_aqi": avg_aqi,
            "duration": route["duration"],
            "distance": route["distance"],
            "exposure": exposure,
            "coordinates": route["coordinates"]
        })

    if not analyzed:
        return None

    fastest = min(analyzed, key=lambda x: x["duration"])
    cleanest = min(analyzed, key=lambda x: x["exposure"])

    return {
        "fastest": fastest,
        "cleanest": cleanest
    }
