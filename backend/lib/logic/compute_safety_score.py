import math
import logging

logger = logging.getLogger(__name__)

def compute_safety_score(edge: dict, traffic_incidents: list, weather_factor: float):
    """
    Computes a safety score for a road segment based on traffic, weather,
    and road type factors.
    
    Args:
        edge (dict): A dictionary representing the road segment.
        traffic_incidents (list): A list of nearby traffic incidents.
        weather_factor (float): The pre-computed weather safety factor.
        
    Returns:
        float: The final safety score.
    """
    # Map incident categories to safety score weights
    incident_weights = {
        1: 1.2,  # Unknown
        9: 1.2,  # Broken-down vehicle
        10: 1.2, # Congestion
        11: 1.2, # Slowdown
        2: 1.5,  # Road closure
        3: 1.5,  # Lane restriction
        5: 1.5,  # Planned event
        6: 1.5,  # Construction
        8: 2.0,  # Accident
        7: 1.8,  # Weather
        4: 1.5   # Other
    }

    road_type = edge.get("type", "road")
    # A motorway is generally safer than a regular road due to design
    accident_risk = 0.5 if "motorway" in road_type or "primary" in road_type else 1.0

    traffic_factor = 1.0
    
    edge_lon = edge["from"]["lon"]
    edge_lat = edge["from"]["lat"]

    for incident in traffic_incidents:
        try:
            category = incident["properties"]["iconCategory"]
            incident_risk = incident_weights.get(category, 1.0)
            
            for coords in incident["geometry"]["coordinates"]:
                incident_lon = coords[0]
                incident_lat = coords[1]
                
                # Use a more robust distance calculation
                distance = math.sqrt((incident_lon - edge_lon)**2 + (incident_lat - edge_lat)**2)

                # Check if the incident is within a small radius (e.g., 0.01 degrees)
                if distance < 0.01:
                    traffic_factor = max(traffic_factor, incident_risk)
                    break # Stop checking other coordinates for this incident
        except Exception as e:
            logger.warning(f"Traffic incident parse error: {e}")
            continue

    
    # Combine factors; higher is worse
    return traffic_factor * weather_factor * accident_risk
            