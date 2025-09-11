import logging
import math
from backend.lib.logic.compute_safety_score import compute_safety_score
from backend.lib.helper.prefetch_route_delays import prefetch_route_delays

logger = logging.getLogger(__name__)

def get_road_class_for_index(details, idx):
    """
    Given the details['road_class'] list and a point index, return the road class for that segment.
    """
    for start, end, road_class in details.get("road_class", []):
        if start <= idx < end:
            return road_class
    return "unclassified"  # default if not found



def get_final_route(routes: list, traffic_incidents: list, weather_factor: float):
    """
    Computes the safety score for each route and returns the safest one.
    Now prefetches per-route traffic delays concurrently to reduce latency.
    """
    safest_route = None
    min_total_score = float("inf")

    # Prefetch traffic delays outside scoring loop
    traffic_delays = prefetch_route_delays(routes)

    for idx, route in enumerate(routes):
        total_score = 0
        coordinates = route.get("points", {}).get("coordinates", [])
        if not coordinates:
            logger.warning(f"Route {idx} has no points, skipping.")
            continue
        details = route.get("details", {})

        traffic_flow_delay = traffic_delays[idx]
        traffic_flow_delay = math.log(1 + (traffic_flow_delay / 60.0))

        for point_idx in range(len(coordinates) - 1):
            road_class = get_road_class_for_index(details, point_idx)
            edge = {
                "from": {"lat": coordinates[point_idx][1], "lon": coordinates[point_idx][0]},
                "to": {"lat": coordinates[point_idx + 1][1], "lon": coordinates[point_idx + 1][0]},
                "type": road_class,
            }
            score = compute_safety_score(edge, traffic_incidents, weather_factor)
            total_score += score * route["distance"] / max(len(coordinates), 1)

        total_score = total_score * traffic_flow_delay
        logger.info(f"Route {idx} total safety score: {total_score}")

        if total_score < min_total_score:
            min_total_score = total_score
            safest_route = route

    return safest_route, min_total_score
