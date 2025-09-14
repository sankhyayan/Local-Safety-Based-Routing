## Safety Route – AI Coding Assistant Instructions

Purpose: Give AI agents the minimum domain + workflow context to be productive without guesswork. Keep changes surgical; do not introduce broad refactors unless explicitly requested.

### Architecture Snapshot
Backend (`backend/`): FastAPI service exposing `/safest-route` (see `backend/main.py`). Orchestrates: (1) route alternatives from GraphHopper (`lib/services/graphhopper_routing.py`), (2) concurrent live data fetch (`lib/helper/live_data.py`), (3) safety scoring pipeline (`lib/logic/get_safest_routes.py` → `compute_safety_score.py`).
Data Sources: GraphHopper (local Java server, profiles under `graphhopper/`), TomTom Traffic (incidents + per-route delays), OpenWeather (weather factor). Frontend: static Leaflet client (`frontend/`). Semantic experimentation lives in `semanticAnalysis/` and is currently isolated (no direct imports into backend).

### Request → Response Flow (`/safest-route`)
1. Input query params: `start_lat,start_lon,end_lat,end_lon` (all required floats).
2. `get_routes_from_graphhopper` POSTs to `${GRAPHHOPPER_URL or http://localhost:8989}/route` with `algorithm=alternative_route` and collects up to 3 alternatives + selects fastest.
3. `fetch_all_live_data` concurrently: (a) TomTom incidents (bounding box), (b) OpenWeather mid-point weather factor.
4. `prefetch_route_delays` concurrently fetches per-route traffic delays via TomTom Routing API, returning seconds (None → 1). Delay is log-transformed and multiplicatively applied.
5. For each route: iterate coordinates pairs, derive road class from `details['road_class']` ranges, build edge dict, compute per-edge score (`compute_safety_score`). Aggregate scaled by `route['distance']/len(points)` then multiply by traffic delay factor. Lowest total = safest.
6. Response includes `safest_route`, `score`, and `debug` with raw incidents + weather factor (note: incidents list can be large—avoid expanding unless user needs it).

### Safety Scoring Notes
`compute_safety_score` combines: incident proximity (category → weight mapping), weather factor (precomputed), road class heuristic (motorway/primary lowers base risk). Distance check uses simple Euclidean on lat/lon (not haversine)—keep consistent unless asked to improve (then adjust tests & docs). Higher numeric score = less safe (we pick min). Multiplicative model: traffic_factor * weather_factor * accident_risk.

### Concurrency & Performance
- Live data and per-route delays use `ThreadPoolExecutor`; keep network calls IO-bound.
- When adding new external calls, prefer parallel fetch patterns consistent with `fetch_all_live_data` / `prefetch_route_delays`.
- Avoid per-point external API calls inside the scoring loop.

### Environment & Configuration
Expected `.env` in `backend/` with: `TOMTOM_API_KEY`, `OPENWEATHER_API_KEY`, optional `GRAPHHOPPER_URL`.
Some service modules currently call `load_dotenv(dotenv_path="backend/.env")` individually; if centralizing, ensure backward compatibility (do not remove without updating all imports).
GraphHopper Java server must be started separately (`java -jar graphhopper-web.jar server config.yaml` in `graphhopper/`). Profiles are custom JSON files (e.g., `chandigarh_*`). The backend currently hardcodes `profile="car_avoid_traffic"`—if making dynamic, add query param sanitation + fallbacks.

### Common Extension Tasks
- Add new safety factor: compute once per route (or per edge if cheap) and integrate multiplicatively or additively—document choice. Keep final selection criterion (min score) unless semantics change.
- Add caching: Safe place is around GraphHopper route call or TomTom incident fetch keyed by rounded bbox and timestamp window. Avoid caching live weather longer than a few minutes without config.
- Improve distance metric: Replace Euclidean with haversine uniformly; update `compute_safety_score` and adjust radius threshold (<0.01 deg) to meters.

### Patterns & Conventions
- Minimal global state; functions are pure where practical.
- Logging: use `logger` per module; do not introduce `print` (some legacy debug prints exist—may remove in cleanup PRs, but don’t rely on them).
- Return shape stability: Preserve keys in `/safest-route` response; add new fields under `debug` to avoid breaking consumers.
- Error handling: Upstream failures (GraphHopper/traffic/weather) degrade gracefully: routes None → 500, missing live data → neutral defaults (empty incidents, weather_factor=1.0, delay=1).

### Frontend Expectations
Frontend expects GeoJSON-like `points.coordinates` (lon,lat pairs) and may render `instructions` if present. Do not reorder coordinate axes. When adding properties, keep existing structure.

### SemanticAnalysis Folder
Independent experimentation (embeddings, LLM). Do not import heavy transformer libs into runtime backend path. Keep new scripts self-contained; use `.venv` isolation as described in its README.

### PR / Change Guidance for AI
Be surgical: modify only necessary modules; avoid mass reformatting. Provide rationale in commit messages (e.g., “Add dynamic routing profile selection with whitelist validation”). Prefer small cohesive changes.

### Quick Dev Commands (Windows PowerShell)
```
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
cd graphhopper; java -jar graphhopper-web.jar server config.yaml
# In new shell (after env + keys set):
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### When Unsure
Ask for: desired scoring direction (min vs max), acceptable latency budget, or whether to expose new parameters via API. Do not introduce breaking API changes silently.

---
Last updated: 2025-09-14