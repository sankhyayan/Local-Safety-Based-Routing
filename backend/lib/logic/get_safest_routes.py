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
    """Compute safety score for each route.

    Returns a list sorted by ascending safety score where each element is:
        {
            "route": <original route dict>,
            "score": <float safety score>,
            "index": <int original index>,
            "traffic_delay_factor": <float applied traffic factor>
        }

    Still uses prefetch_route_delays for efficiency.
    """
    ranked = []

    if not routes:
        return ranked

    traffic_delays = prefetch_route_delays(routes)

    for idx, route in enumerate(routes):
        coordinates = route.get("points", {}).get("coordinates", [])
        if not coordinates:
            logger.warning(f"Route {idx} has no points, skipping.")
            continue
        details = route.get("details", {})

        raw_delay = traffic_delays[idx]
        traffic_flow_factor = math.log(1 + (raw_delay / 60.0))

        distance = route.get("distance", 0) or 0
        total_score = 0.0
        segment_count = max(len(coordinates) - 1, 1)

        for point_idx in range(segment_count):
            road_class = get_road_class_for_index(details, point_idx)
            edge = {
                "from": {"lat": coordinates[point_idx][1], "lon": coordinates[point_idx][0]},
                "to": {"lat": coordinates[point_idx + 1][1], "lon": coordinates[point_idx + 1][0]},
                "type": road_class,
            }
            score = compute_safety_score(edge, traffic_incidents, weather_factor)
            # Weight by route distance / number of segments to normalize
            total_score += score * (distance / segment_count if segment_count else 1)

        total_score *= traffic_flow_factor
        ranked.append({
            "route": route,
            "score": total_score,
            "index": idx,
            "traffic_delay_factor": traffic_flow_factor,
        })

    ranked.sort(key=lambda r: r["score"])  # lower is safer
    logger.info("Ranked routes (index: score): %s", [f"{r['index']}: {r['score']:.3f}" for r in ranked])
    return ranked
