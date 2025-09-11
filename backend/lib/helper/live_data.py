import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.lib.services.fetch_incidents import fetch_live_incidents
from backend.lib.services.fetch_weather import fetch_weather


logger = logging.getLogger(__name__)

def fetch_all_live_data(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    """Fetch traffic incidents and weather concurrently to reduce latency."""
    min_lat, max_lat = min(start_lat, end_lat), max(start_lat, end_lat)
    min_lon, max_lon = min(start_lon, end_lon), max(start_lon, end_lon)
    bbox = f"{min_lon},{min_lat},{max_lon},{max_lat}"
    mid_lat, mid_lon = (start_lat + end_lat) / 2, (start_lon + end_lon) / 2

    traffic_incidents = []
    weather_factor = 1.0

    with ThreadPoolExecutor(max_workers=2) as executor:
        fut_inc = executor.submit(fetch_live_incidents, bbox)
        fut_weather = executor.submit(fetch_weather, mid_lat, mid_lon)
        for fut in as_completed([fut_inc, fut_weather]):
            try:
                result = fut.result()
                if fut is fut_inc:
                    traffic_incidents = result or []
                else:
                    weather_factor = float(result) if result is not None else 1.0
            except Exception as e:
                logger.warning(f"Live data fetch sub-task failed: {e}")

    logger.info(
        "Live data fetched concurrently: incidents=%d, weather_factor=%s", 
        len(traffic_incidents), weather_factor
    )
    return traffic_incidents, weather_factor

