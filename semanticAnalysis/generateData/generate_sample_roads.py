import json
import csv
import random
from pathlib import Path
from typing import List, Dict, Any

# Chandigarh rough bounding box (lon, lat)
MIN_LON, MAX_LON = 76.70, 76.85
MIN_LAT, MAX_LAT = 30.67, 30.77

ROAD_CLASSES = [
    "motorway", "primary", "secondary", "tertiary", "residential",
    "service", "trunk", "unclassified", "footway", "cycleway"
]

SURFACES = ["paved", "asphalt", "concrete", "gravel", "dirt", "cobblestone"]
WEATHER_TAGS = ["clear", "rain", "heavy_rain", "fog", "smog", "storm", "drizzle"]
INCIDENT_TYPES = [
    {"iconCategory": 8, "label": "accident"},
    {"iconCategory": 6, "label": "construction"},
    {"iconCategory": 10, "label": "congestion"},
    {"iconCategory": 11, "label": "slowdown"},
    {"iconCategory": 2, "label": "closure"},
    {"iconCategory": 7, "label": "weather"},
]

random.seed(42)


def rand_coord():
    return round(random.uniform(MIN_LAT, MAX_LAT), 6), round(random.uniform(MIN_LON, MAX_LON), 6)


def generate_record(idx: int) -> Dict[str, Any]:
    start_lat, start_lon = rand_coord()
    end_lat = min(MAX_LAT, max(MIN_LAT, start_lat + random.uniform(-0.003, 0.003)))
    end_lon = min(MAX_LON, max(MIN_LON, start_lon + random.uniform(-0.003, 0.003)))
    distance_m = random.randint(80, 3500)
    road_class = random.choice(ROAD_CLASSES)
    surface = random.choice(SURFACES)

    # Simulate traffic incidents near start point with probability
    incident_count = 0
    incidents: List[Dict[str, Any]] = []
    if random.random() < 0.55:
        incident_count = random.randint(1, 3)
        for _ in range(incident_count):
            it = random.choice(INCIDENT_TYPES)
            incidents.append({
                "properties": {"iconCategory": it["iconCategory"], "label": it["label"]},
                "geometry": {"type": "Point", "coordinates": [start_lon + random.uniform(-0.001, 0.001), start_lat + random.uniform(-0.001, 0.001)]}
            })

    weather = random.choice(WEATHER_TAGS)

    # Map weather to a factor similar to compute logic
    weather_factor = 1.0
    if weather in ["storm"]:
        weather_factor += 1.0
    elif weather in ["heavy_rain"]:
        weather_factor += 0.7
    elif weather in ["rain", "drizzle"]:
        weather_factor += 0.4
    elif weather in ["fog", "smog"]:
        weather_factor += 0.5

    # Base incident risk multiplier
    incident_multiplier = 1.0
    for inc in incidents:
        cat = inc["properties"]["iconCategory"]
        if cat == 8:
            incident_multiplier = max(incident_multiplier, 2.0)
        elif cat in (6, 2, 3, 5, 4):
            incident_multiplier = max(incident_multiplier, 1.5)
        elif cat in (10, 11, 1, 9):
            incident_multiplier = max(incident_multiplier, 1.2)
        elif cat == 7:
            incident_multiplier = max(incident_multiplier, 1.8)

    # Road safety baseline (motorway/primary considered safer => lower risk factor)
    accident_risk = 0.5 if ("motorway" in road_class or "primary" in road_class) else 1.0

    safety_score = round(incident_multiplier * weather_factor * accident_risk, 3)

    text_description = (
        f"Road segment {idx} classified as {road_class} with {surface} surface, "
        f"distance {distance_m}m from ({start_lat},{start_lon}) to ({end_lat},{end_lon}). "
        f"Weather: {weather}. Incidents: {incident_count}. Estimated safety score: {safety_score}."
    )

    return {
        "id": idx,
        "start_lat": start_lat,
        "start_lon": start_lon,
        "end_lat": end_lat,
        "end_lon": end_lon,
        "distance_m": distance_m,
        "road_class": road_class,
        "surface": surface,
        "weather": weather,
        "incident_count": incident_count,
        "incidents": incidents,
        "weather_factor": round(weather_factor, 3),
        "incident_multiplier": round(incident_multiplier, 3),
        "accident_risk": accident_risk,
        "safety_score": safety_score,
        "text": text_description,
    }


def generate_dataset(n: int = 100) -> List[Dict[str, Any]]:
    return [generate_record(i) for i in range(1, n + 1)]


def write_jsonl(path: Path, rows: List[Dict[str, Any]]):
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: List[Dict[str, Any]]):
    fieldnames = [
        "id", "start_lat", "start_lon", "end_lat", "end_lon", "distance_m",
        "road_class", "surface", "weather", "incident_count", "weather_factor",
        "incident_multiplier", "accident_risk", "safety_score", "text"
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            slim = {k: r.get(k) for k in fieldnames}
            writer.writerow(slim)


def main():
    base = Path(__file__).parent / "data"
    base.mkdir(exist_ok=True, parents=True)
    rows = generate_dataset(100)
    write_jsonl(base / "chandigarh_roads_sample.jsonl", rows)
    write_csv(base / "chandigarh_roads_sample.csv", rows)
    print("Generated: jsonl & csv in", base)

if __name__ == "__main__":
    main()
