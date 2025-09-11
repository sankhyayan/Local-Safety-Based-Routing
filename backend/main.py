import logging
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.lib.services.graphhopper_routing import get_routes_from_graphhopper
from backend.lib.helper.live_data import fetch_all_live_data
from backend.lib.logic.get_safest_routes import get_final_route

# -------------------- Setup --------------------
load_dotenv()
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------- Endpoint --------------------

@app.get("/safest-route")
async def get_safest_route(
    start_lat: float = Query(...),
    start_lon: float = Query(...),
    end_lat: float = Query(...),
    end_lon: float = Query(...)
):
    """
    Computes the safest route by evaluating multiple routes from GraphHopper
    against live weather and traffic data.
    """
    # Step 1: Query GraphHopper for multiple route alternatives
    routes, fastest_route = get_routes_from_graphhopper(start_lat, start_lon, end_lat, end_lon)
    if routes is None:
        return JSONResponse(status_code=500, content={"error": "GraphHopper API failed or no routes found"})

    # Step 2: Fetch live data
    traffic_incidents, weather_factor = fetch_all_live_data(start_lat, start_lon, end_lat, end_lon)


    # Step 3: Compute safety score for each route
    safest_route, min_total_score = get_final_route(routes, traffic_incidents, weather_factor)

    # Step 4: Handle fallback
    if safest_route is None:
        return {
            "message": "Safest route could not be computed, returning fastest route as fallback.",
            "safest_route": fastest_route,
            "score": None,
            "debug": {
                "routes_found": len(routes),
                "traffic_incidents": len(traffic_incidents),
                "weather_factor": weather_factor,
            }
        }

    # Step 5: Final Response
    return {
        "safest_route": safest_route,
        "score": min_total_score,
        "debug": {
            "routes_found": len(routes),
            "traffic_incidents": traffic_incidents,
            "weather_factor": weather_factor,
        }
    }
