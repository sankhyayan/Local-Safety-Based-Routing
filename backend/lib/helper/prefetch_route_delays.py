import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from backend.lib.services.fetch_traffic_delays import fetch_route_delays

logger = logging.getLogger(__name__)


def prefetch_route_delays(routes: list, *, max_workers: int = 4) -> List[int]:
    """Fetch traffic flow delay for each route concurrently.
    Returns a list aligned with routes; missing/failed -> 1 (minimum).
    Each route object is expected to have GraphHopper structure with
    route['points']['coordinates'] as [ [lon, lat], ... ].
    """
    traffic_delays: List[int] = [1] * len(routes)

    def task(i: int, coords):
        try:
            delay = fetch_route_delays(coords, traffic=True, section_traffic=True)
            if not isinstance(delay, (int, float)) or delay is None:
                return i, 1
            return i, max(int(delay), 1)
        except Exception as e:  # noqa: BLE001 (broad ok for isolation)
            logger.debug("Delay fetch failed for route %d: %s", i, e)
            return i, 1

    # Avoid spawning more workers than routes
    worker_count = min(max_workers, len(routes) or 1)
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = []
        for i, r in enumerate(routes):
            coords = r.get("points", {}).get("coordinates", [])
            if not coords or len(coords) < 2:
                continue
            futures.append(executor.submit(task, i, coords))
        for fut in as_completed(futures):
            idx, val = fut.result()
            traffic_delays[idx] = val

    return traffic_delays
