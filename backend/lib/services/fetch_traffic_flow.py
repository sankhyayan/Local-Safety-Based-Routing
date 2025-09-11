import logging
import os
from typing import Any, Dict, List, Sequence, Tuple

import requests

logger = logging.getLogger(__name__)


def _get_api_key() -> str | None:
	return os.getenv("TOMTOM_API_KEY")


def fetch_traffic_flow(
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

	# Determine first (start) and last (end) coordinates
	start_lon, start_lat = coords[0]
	end_lon, end_lat = coords[-1]


	# Build URL path with start and end in lat,lon order
	url = f"https://api.tomtom.com/routing/1/calculateRoute/{start_lat},{start_lon}:{end_lat},{end_lon}/json"
	params = {
		"key": api_key,
		"traffic": "true" if traffic else "false",
		"computeTravelTimeFor": "all" if traffic else "none",
		"routeRepresentation": "summaryOnly",
		"travelMode": "car",
	}
	if section_traffic:
		params["sectionType"] = "traffic"

	body = {
		"supportingPoints": [{"latitude": lat, "longitude": lon} for lon, lat in coords],
	}

	try:
		resp = requests.post(url, params=params, json=body, timeout=30)
		if resp.status_code != 200:
			logger.error("TomTom API error %s: %s", resp.status_code, resp.text[:500])
			return None

		data = resp.json()
		traffic_flow_delay = (data.get("routes") or [{}])[0].get("summary", {}).get("trafficDelayInSeconds")
		print(f"traffic flow delay: {traffic_flow_delay}")
		return traffic_flow_delay
	
	except requests.RequestException as e:
		logger.exception("TomTom API request failed: %s", e)
		return None


