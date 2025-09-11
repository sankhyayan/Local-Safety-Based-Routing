import os
import logging
from dotenv import load_dotenv
import requests

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load .env from backend directory
load_dotenv(dotenv_path="backend/.env")

# Debug: Check if .env file loads
print(f"Current working directory: {os.getcwd()}")
print(f"Environment variables loaded:")
print(f"TOMTOM_API_KEY exists: {'TOMTOM_API_KEY' in os.environ}")

TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")
print(f"TOMTOM_API_KEY value: {TOMTOM_API_KEY}")

def fetch_live_incidents(bbox: str):
    """
    Fetches live traffic incidents from the TomTom API.
    
    Args:
        bbox (str): The bounding box string (e.g., "lon1,lat1,lon2,lat2").
        
    Returns:
        list: A list of traffic incidents or an empty list if an error occurs.
    """

    print(f"TOmTOM: {TOMTOM_API_KEY}")
    if not TOMTOM_API_KEY:
        logger.warning("TomTom API key missing.")
        return []
    
    
    # URL-encoded fields parameter
    encoded_fields = "%7Bincidents%7Btype,geometry%7Btype,coordinates%7D,properties%7BiconCategory%7D%7D%7D"
    
    # Construct the URL with the encoded fields
    url = f"https://api.tomtom.com/traffic/services/5/incidentDetails?bbox={bbox}&fields={encoded_fields}&language=en-US&timeValidityFilter=present&key={TOMTOM_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Traffic data fetched successfully.")
        return data.get("incidents", [])
    except Exception as e:
        logger.error(f"Traffic API error: {e}")
        return []
