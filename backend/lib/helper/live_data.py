import logging

from backend.lib.services.fetch_traffic import fetch_live_incidents
from backend.lib.services.fetch_weather import fetch_weather


logger = logging.getLogger(__name__)

def fetch_all_live_data(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    """
    Fetches live traffic and weather data for the route's bounding box.
    Returns the traffic incidents and weather factor.
    """
    min_lat, max_lat = min(start_lat, end_lat), max(start_lat, end_lat)
    min_lon, max_lon = min(start_lon, end_lon), max(start_lon, end_lon)
    bbox = f"{min_lon},{min_lat},{max_lon},{max_lat}"

    traffic_incidents = fetch_live_incidents(bbox)
    mid_lat, mid_lon = (start_lat + end_lat) / 2, (start_lon + end_lon) / 2
    weather_factor = fetch_weather(mid_lat, mid_lon)

    logger.info(f"Traffic incidents found: {len(traffic_incidents)}, Weather factor: {weather_factor}")
    return traffic_incidents, weather_factor
