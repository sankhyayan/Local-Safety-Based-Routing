import os
import requests
import logging

logger = logging.getLogger(__name__)
GRAPHHOPPER_URL = os.getenv("GRAPHHOPPER_URL", "http://localhost:8989")

def get_routes_from_graphhopper(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    """
    Queries GraphHopper for multiple route alternatives.
    Returns the list of routes and the fastest route.
    """
    try:
        gh_params = {
            "points": [[start_lon, start_lat], [end_lon, end_lat]], # Corrected `end_lat`
            "profile": "car_avoid_traffic", # TODO make dynamic
            "details": ["road_class", "max_speed"],
            "points_encoded": False,
            "algorithm":"alternative_route",
            "alternative_route.max_paths": 3,
            "alternative_route.max_weight_factor": 1.5
        }
        gh_response = requests.post(f"{GRAPHHOPPER_URL}/route", json=gh_params, timeout=15)
        gh_response.raise_for_status()
        gh_data = gh_response.json()
        
        routes = gh_data.get("paths", [])
        if not routes:
            return None, None
        logger.info(f"GraphHopper returned {len(routes)} routes")
        leastTime = float('inf')
        fastest_route = None
        for route in routes:
            if route["time"] < leastTime:
                leastTime = route["time"]
                fastest_route = route

        return routes, fastest_route

    except Exception as e:
        logger.error(f"GraphHopper API error: {e}")
        return None, None
