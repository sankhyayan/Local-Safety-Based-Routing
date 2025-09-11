import logging
import os
from typing import Any, Dict, List

import requests

logger = logging.getLogger(__name__)


def fetch_routes_with_tomtom_traffic(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    max_alternatives: int = 2,
) -> List[Dict[str, Any]]:
    """
    Calls TomTom Routes API with traffic enabled and returns a list of routes
    with summarized traffic information per route.

    Returns a list like:
    [
      {
        "index": 0,
        "summary": {
          "length_m": int,
          "travel_time_s": int,
          "no_traffic_time_s": int,
          "traffic_delay_s": int
        },
        "sections": [
          {"type": "TRAFFIC", "delay_s": int} ...
        ]
      }, ...
    ]

    Notes:
    - Requires TOMTOM_API_KEY in environment.
    - Uses summary-only representation to keep payload small.
    """
    api_key = os.getenv("TOMTOM_API_KEY")
    if not api_key:
        logger.warning("TOMTOM_API_KEY not set; skipping TomTom traffic fetch.")
        return []

    base_url = "https://api.tomtom.com/routing/1/calculateRoute"
    # TomTom location path format: "lat,lon:lat,lon"
    locations = f"{start_lat},{start_lon}:{end_lat},{end_lon}"
    url = f"{base_url}/{locations}/json"
    params = {
        "key": api_key,
        "traffic": "true",
        "routeRepresentation": "summaryOnly",
        "computeTravelTimeFor": "all",
        "maxAlternatives": str(max(0, min(max_alternatives, 5))),
        "sectionType": "TRAFFIC",
        "travelMode": "car",
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code != 200:
            logger.error("TomTom API error %s: %s", resp.status_code, resp.text[:500])
            return []
        data = resp.json()
        routes = data.get("routes", []) or []
        results: List[Dict[str, Any]] = []
        for idx, r in enumerate(routes):
            summary = r.get("summary", {}) or {}
            sections = r.get("sections", []) or []
            traffic_sections = []
            for s in sections:
                if s.get("type") == "TRAFFIC":
                    traffic_info = s.get("traffic", {}) or {}
                    traffic_sections.append({
                        "type": s.get("type"),
                        "delay_s": traffic_info.get("delayInSeconds"),
                    })
            results.append({
                "index": idx,
                "summary": {
                    "length_m": summary.get("lengthInMeters"),
                    "travel_time_s": summary.get("travelTimeInSeconds"),
                    "no_traffic_time_s": summary.get("noTrafficTravelTimeInSeconds"),
                    "traffic_delay_s": summary.get("trafficDelayInSeconds"),
                },
                "sections": traffic_sections,
            })
        return results
    except requests.RequestException as e:
        logger.exception("TomTom API request failed: %s", e)
        return []
