import logging
import os
from typing import Any, Dict, List, Sequence, Tuple

import requests

logger = logging.getLogger(__name__)


def _get_api_key() -> str | None:
	return os.getenv("TOMTOM_API_KEY")


def fetch_routes_with_tomtom_traffic(
	start_lat: float,
	start_lon: float,
	end_lat: float,
	end_lon: float,
	max_alternatives: int = 2,
) -> List[Dict[str, Any]]:
	"""
	Calls TomTom Routes API (POST) with traffic enabled and returns a list of route
	summaries with traffic delay stats. This version uses simple start/end.
	"""
	api_key = _get_api_key()
	if not api_key:
		logger.warning("TOMTOM_API_KEY not set; skipping TomTom traffic fetch.")
		return []

	url = "https://api.tomtom.com/routing/1/calculateRoute/json"
	params = {
		"key": api_key,
		"traffic": "true",
		"routeRepresentation": "summaryOnly",
		"computeTravelTimeFor": "all",
		"maxAlternatives": str(max(0, min(max_alternatives, 5))),
		"sectionType": "TRAFFIC",
		"travelMode": "car",
	}
	body = {
		"locations": [
			{"lat": start_lat, "lon": start_lon},
			{"lat": end_lat, "lon": end_lon},
		]
	}

	try:
		resp = requests.post(url, params=params, json=body, timeout=20)
		if resp.status_code != 200:
			logger.error("TomTom API error %s: %s", resp.status_code, resp.text[:500])
			return []
		return _parse_tomtom_routes(resp.json())
	except requests.RequestException as e:
		logger.exception("TomTom API request failed: %s", e)
		return []


def fetch_routes_with_tomtom_traffic_waypoints(
	coords: Sequence[Tuple[float, float]],
	*,
	traffic: bool = True,
	section_traffic: bool = True,
) -> Dict[str, Any] | None:
	"""
	Calculate a route strictly following the provided waypoints (ordered lat, lon tuples)
	using POST to avoid URL limits. Returns the full TomTom response JSON.
	"""
	api_key = _get_api_key()
	if not api_key:
		logger.warning("TOMTOM_API_KEY not set; skipping TomTom traffic fetch.")
		return None

	if not coords or len(coords) < 2:
		logger.warning("At least 2 coordinates are required (start and end).")
		return None

	url = "https://api.tomtom.com/routing/1/calculateRoute/json"
	params = {
		"key": api_key,
		"traffic": "true" if traffic else "false",
		"computeTravelTimeFor": "all" if traffic else "none",
		"routeRepresentation": "summaryOnly",
		"travelMode": "car",
	}
	if section_traffic:
		params["sectionType"] = "TRAFFIC"

	body = {
		"locations": [{"lat": lat, "lon": lon} for lat, lon in coords],
	}

	try:
		resp = requests.post(url, params=params, json=body, timeout=30)
		if resp.status_code != 200:
			logger.error("TomTom API error %s: %s", resp.status_code, resp.text[:500])
			return None
		return resp.json()
	except requests.RequestException as e:
		logger.exception("TomTom API request failed: %s", e)
		return None


def _parse_tomtom_routes(data: Dict[str, Any]) -> List[Dict[str, Any]]:
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

