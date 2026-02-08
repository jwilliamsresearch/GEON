"""Convert GeoJSON features to GEON format.

Demonstrates converting both Point and Polygon GeoJSON features,
including FeatureCollections.

No external dependencies required.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import geon

# ── 1. Point feature ──────────────────────────────────────────────────────

point_geojson = {
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [-1.8984, 52.4774],
    },
    "properties": {
        "name": "Birmingham New Street Station",
        "railway": "station",
        "operator": "Network Rail",
        "amenity": "rail transport",
    },
}

place = geon.from_geojson(point_geojson)
print("=== Point Feature -> GEON ===")
print(geon.generate(place))

# ── 2. Polygon feature ───────────────────────────────────────────────────

polygon_geojson = {
    "type": "Feature",
    "geometry": {
        "type": "Polygon",
        "coordinates": [[
            [-1.8940, 52.4780],
            [-1.8926, 52.4780],
            [-1.8926, 52.4774],
            [-1.8940, 52.4774],
            [-1.8940, 52.4780],
        ]],
    },
    "properties": {
        "name": "Birmingham Bullring Markets",
        "leisure": "marketplace",
        "shop": "general",
        "experience": {
            "openness": "medium",
            "activity_density": "high",
            "noise_level": "loud",
        },
    },
}

place2 = geon.from_geojson(polygon_geojson)
print("=== Polygon Feature -> GEON ===")
print(geon.generate(place2))

# ── 3. FeatureCollection ─────────────────────────────────────────────────

collection = {
    "type": "FeatureCollection",
    "features": [point_geojson, polygon_geojson],
}

places = geon.from_geojson(collection)
print(f"=== FeatureCollection -> {len(places)} GEON places ===")
for p in places:
    print(f"  - {p.place} ({p.type})")
print()

# ── 4. Round-trip: GeoJSON → GEON → GeoJSON ──────────────────────────────

print("=== Round-trip: GEON -> GeoJSON ===")
back = geon.to_geojson_string(places, indent=2)
print(back)
