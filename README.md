# 🛣️ Safety Route

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)
![GraphHopper](https://img.shields.io/badge/GraphHopper-10.2+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**An intelligent route planning system that prioritizes safety over speed**

[Features](#features) • [Demo](#demo) • [Installation](#installation) • [API](#api) • [Contributing](#contributing)

</div>

---

## 🎯 Overview

Safety Route is a smart navigation system that calculates the **safest possible routes** instead of just the fastest ones. By analyzing real-time traffic incidents, weather conditions, and road types, it helps you reach your destination safely.

### 🌟 Key Features

- **🛡️ Safety-First Routing** - Prioritizes safety over speed using advanced scoring algorithms
- **🌦️ Real-Time Weather Integration** - Adjusts routes based on current weather conditions
- **🚗 Live Traffic Analysis** - Incorporates real-time traffic incidents and road closures
- **🗺️ Multiple Route Options** - Provides balanced, fast, and traffic-avoiding route variants
- **📍 Interactive Maps** - Beautiful web interface with Leaflet.js integration
- **⚡ Fast API** - Built with FastAPI for high-performance routing

---

## 🚀 Demo

<div align="center">
  <img src="https://via.placeholder.com/800x400/2196F3/ffffff?text=Safety+Route+Demo" alt="Safety Route Demo" style="border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
</div>

> **Try it live:** [Demo Link](#) *(Coming Soon)*

---

## 🏗️ Architecture

```
Safety Route/
├── 🎨 frontend/           # Interactive web interface
│   ├── index.html         # Main application page
│   ├── script.js          # Frontend logic & map integration
│   └── style.css          # Beautiful UI styling
│
├── ⚙️ backend/            # FastAPI backend service
│   ├── main.py           # API server & route endpoints
│   ├── .env              # Environment variables
│   └── lib/              # Core logic modules
│       ├── logic/        # Route computation & safety scoring
│       └── services/     # External API integrations
│
└── 🗺️ graphhopper/       # Route calculation engine
    ├── config.yaml       # GraphHopper configuration
    ├── *.json            # Custom routing profiles
    └── chandigarh.osm.pbf # OpenStreetMap data
```

---

## 🛠️ Installation

### Prerequisites

- **Python 3.8+**
- **Java 11+** (for GraphHopper)
- **API Keys** for TomTom Traffic & OpenWeather

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/safety-route.git
   cd safety-route
   ```

2. **Set up Python environment**
   ```bash
   python -m venv safety_venv
   source safety_venv/bin/activate  # On Windows: safety_venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   # Create backend/.env file
   TOMTOM_API_KEY=your_tomtom_api_key
   OPENWEATHER_API_KEY=your_openweather_api_key
   ```

4. **Download & prepare map data**
   ```bash
   # Download Chandigarh OSM data
   wget https://download.geofabrik.de/asia/india/chandigarh-latest.osm.pbf
   mv chandigarh-latest.osm.pbf graphhopper/chandigarh.osm.pbf
   ```

5. **Start GraphHopper server**
   ```bash
   cd graphhopper
   java -jar graphhopper-web.jar server config.yaml
   ```

6. **Launch the API server**
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Open the web app**
   ```bash
   # Open frontend/index.html in your browser
   # or serve it with a simple HTTP server
   cd frontend
   python -m http.server 3000
   ```

---

## 📊 How It Works

### Safety Scoring Algorithm

Our intelligent routing system evaluates routes based on multiple safety factors:

```python
# Simplified safety calculation
safety_score = (
    road_type_safety * 0.4 +      # Road classification weight
    traffic_incident_penalty +     # Live incident data
    weather_safety_factor +        # Current conditions
    historical_accident_data       # Long-term safety trends
)
```

### Route Types

| Profile | Description | Use Case |
|---------|-------------|----------|
| 🔄 **Balanced** | Optimal safety-speed trade-off | Daily commuting |
| 🏃 **Fast** | Prioritizes main roads & speed | Emergency situations |
| 🚫 **Traffic-Avoiding** | Uses smaller roads | Heavy congestion periods |
| 🚶 **Pedestrian** | Walking-optimized routes | City exploration |
| 🚴 **Cycling** | Bike-friendly paths | Eco-friendly travel |

---

## 🔌 API Reference

### Get Safest Route

```http
GET /safest-route?start_lat={lat}&start_lon={lon}&end_lat={lat}&end_lon={lon}
```

**Response:**
```json
{
  "safest_route": {
    "distance": 4000.419,
    "time": 298551,
    "points": {
      "coordinates": [[76.779395, 30.733297], ...]
    },
    "instructions": [...]
  },
  "score": 926.71,
  "alternatives": [...]
}
```

### Health Check

```http
GET /health
```

---

## 🤝 Contributing

We love contributions! Here's how you can help:

1. **🍴 Fork the repository**
2. **🌿 Create your feature branch** (`git checkout -b feature/amazing-feature`)
3. **✅ Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **📤 Push to the branch** (`git push origin feature/amazing-feature`)
5. **🔁 Open a Pull Request**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black backend/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[GraphHopper](https://www.graphhopper.com/)** - Open-source routing engine
- **[OpenStreetMap](https://www.openstreetmap.org/)** - Community-driven map data
- **[TomTom](https://developer.tomtom.com/)** - Real-time traffic API
- **[OpenWeather](https://openweathermap.org/)** - Weather data API
- **[Leaflet](https://leafletjs.com/)** - Interactive map library

---

<div align="center">

**Made with ❤️ for safer journeys**

[⭐ Star this repo](https://github.com/yourusername/safety-route) • [🐛 Report Bug](https://github.com/yourusername/safety-route/issues) • [💡 Request Feature](https://github.com/yourusername/safety-route/issues)

</div>