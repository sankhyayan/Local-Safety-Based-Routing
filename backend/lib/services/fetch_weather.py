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
print(f"OPENWEATHER_API_KEY exists: {'OPENWEATHER_API_KEY' in os.environ}")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
print(f"OPENWEATHER_API_KEY value: {OPENWEATHER_API_KEY}")

def fetch_weather(lat: float, lon: float):
    """
    Fetches weather data and computes a safety factor based on conditions.
    
    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        
    Returns:
        float: A safety factor (1.0 for normal conditions, higher for hazards).
    """
    print(f"OpenWeather: {OPENWEATHER_API_KEY}")
    if not OPENWEATHER_API_KEY:
        logger.warning("OpenWeather API key missing.")
        return 1.0
    
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        weather_factor = 1.0
        
        # Check for hazardous weather conditions
        weather_main = data.get("weather", [{}])[0].get("main", "Clear")
        weather_description = data.get("weather", [{}])[0].get("description", "")
        
        if weather_main in ["Thunderstorm", "Tornado"]:
            weather_factor += 1.0
        elif "heavy" in weather_description or weather_main in ["Snow", "Fog"]:
            weather_factor += 0.7
        elif weather_main in ["Rain", "Drizzle"]:
            weather_factor += 0.4
        
        # Check for low visibility (in meters)
        visibility = data.get("visibility", 10000)
        if visibility < 1000:
            weather_factor += 0.6
        elif visibility < 5000:
            weather_factor += 0.3
        
        # Check for high wind speed (in m/s)
        wind_speed = data.get("wind", {}).get("speed", 0)
        if wind_speed > 20:
            weather_factor += 0.5
        elif wind_speed > 10:
            weather_factor += 0.2
            
        # Check for extreme temperatures (in Celsius)
        temp_kelvin = data.get("main", {}).get("temp", 273)
        temp_celsius = temp_kelvin - 273.15
        if temp_celsius < 0 or temp_celsius > 40:
            weather_factor += 0.2

        logger.info(f"Weather fetched: {weather_description}, Final factor: {weather_factor}")
        
        return weather_factor
    except requests.exceptions.HTTPError as e:
        logger.error(f"Weather API HTTP error: {e}")
        return 1.0
    except requests.exceptions.RequestException as e:
        logger.error(f"Weather API request error: {e}")
        return 1.0
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1.0
