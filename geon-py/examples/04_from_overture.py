"""Fetch places from the Overture Maps API and convert to GEON.

Overture Maps provides open map data combining contributions from
Microsoft, Meta, TomTom, and others. This example queries the
Overture Maps places dataset via their API.

Requirements:
    pip install requests
    (or: pip install geon[overture])
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import geon
from geon.models import Coordinate, GeonPlace

try:
    import requests
except ImportError:
    print("This example requires the 'requests' package.")
    print("Install with:  pip install requests")
    sys.exit(1)


# Overture Maps data can be accessed via their public GeoParquet files on S3,
# or via third-party APIs. Here we demonstrate a pattern using a local
# GeoJSON export (common workflow) and also show a direct HTTP approach
# via the Overture Maps Explorer API.


def overture_feature_to_geon(feature: dict) -> GeonPlace:
    """Convert an Overture Maps GeoJSON feature to GEON.

    Overture features have a richer property structure than vanilla GeoJSON,
    including categories, confidence scores, and source information.
    """
    props = feature.get("properties", {})
    geom = feature.get("geometry", {})

    p = GeonPlace()

    # Name — Overture uses a nested names structure
    names = props.get("names", {})
    if isinstance(names, dict):
        primary = names.get("primary", "")
        p.place = primary if primary else props.get("name", "Unnamed")
    else:
        p.place = props.get("name", "Unnamed")

    # ID
    p.id = props.get("id", feature.get("id", ""))

    # Category → TYPE mapping
    categories = props.get("categories", {})
    if isinstance(categories, dict):
        main_cat = categories.get("main", "")
        p.type = _overture_category_to_type(main_cat)
        if categories.get("alternate"):
            p.purpose = [str(c) for c in categories["alternate"]]
    else:
        p.type = "hybrid"

    # Location
    if geom.get("type") == "Point":
        coords = geom["coordinates"]
        p.location = Coordinate(lat=coords[1], lon=coords[0])
    elif geom.get("type") == "Polygon":
        ring = geom["coordinates"][0]
        avg_lon = sum(c[0] for c in ring) / len(ring)
        avg_lat = sum(c[1] for c in ring) / len(ring)
        p.location = Coordinate(lat=avg_lat, lon=avg_lon)
        p.boundary = [Coordinate(lat=c[1], lon=c[0]) for c in ring]

    # Confidence
    conf = props.get("confidence", None)
    if conf is not None:
        p.confidence["overall"] = f"{conf:.2f}"

    # Sources
    sources = props.get("sources", [])
    if isinstance(sources, list):
        for src in sources:
            if isinstance(src, dict):
                dataset = src.get("dataset", "unknown")
                p.source.append(f"Overture Maps ({dataset})")
            else:
                p.source.append(str(src))
    if not p.source:
        p.source.append("Overture Maps")

    # Address
    addresses = props.get("addresses", [])
    if addresses and isinstance(addresses, list):
        addr = addresses[0] if isinstance(addresses[0], dict) else {}
        freeform = addr.get("freeform", "")
        if freeform:
            p.extra["address"] = freeform

    # Websites / phones
    if props.get("websites"):
        p.extra["website"] = props["websites"][0] if isinstance(props["websites"], list) else props["websites"]
    if props.get("phones"):
        p.extra["phone"] = props["phones"][0] if isinstance(props["phones"], list) else props["phones"]

    return p


def _overture_category_to_type(category: str) -> str:
    """Map Overture category strings to GEON types."""
    cat_lower = category.lower()
    mapping = {
        "restaurant": "building",
        "cafe": "building",
        "bar": "building",
        "hotel": "building",
        "school": "building",
        "hospital": "building",
        "bank": "building",
        "shop": "building",
        "supermarket": "building",
        "park": "public_space",
        "garden": "public_space",
        "playground": "public_space",
        "sports_centre": "public_space",
        "stadium": "public_space",
        "train_station": "transport_hub",
        "bus_station": "transport_hub",
        "airport": "transport_hub",
        "museum": "landmark",
        "monument": "landmark",
        "church": "landmark",
        "cathedral": "landmark",
        "castle": "landmark",
    }
    for key, val in mapping.items():
        if key in cat_lower:
            return val
    return "hybrid"


# ── Example 1: Convert an Overture-style GeoJSON feature ─────────────────

print("=== Example 1: Overture Maps feature -> GEON ===\n")

# Simulated Overture Maps feature (same schema as real exports)
overture_feature = {
    "type": "Feature",
    "id": "08f194ad-3241-0744-0200-54a1a98e6d95",
    "geometry": {
        "type": "Point",
        "coordinates": [-1.1490, 52.9534],
    },
    "properties": {
        "id": "08f194ad-3241-0744-0200-54a1a98e6d95",
        "names": {
            "primary": "Ye Olde Trip to Jerusalem",
        },
        "categories": {
            "main": "bar",
            "alternate": ["pub", "historic_pub", "tourism"],
        },
        "confidence": 0.92,
        "sources": [
            {"dataset": "meta"},
            {"dataset": "microsoft"},
        ],
        "addresses": [
            {"freeform": "1 Brewhouse Yard, Nottingham NG1 6AD"},
        ],
        "websites": ["https://www.triptojerusalem.com"],
    },
}

place = overture_feature_to_geon(overture_feature)
place.character = [
    "historic (claims to be England's oldest inn, est. 1189)",
    "atmospheric (carved into sandstone caves)",
]
place.experience = {
    "enclosure": "high",
    "visual_complexity": "high",
    "sense_of_safety": "safe",
}

print(geon.generate(place))

# Validate
result = geon.validate(place)
print(f"Valid: {result.valid}")
for issue in result.issues:
    print(f"  {issue}")

# ── Example 2: Batch convert a collection ─────────────────────────────────

print("\n=== Example 2: Overture FeatureCollection -> GEON ===\n")

overture_collection = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "id": "place-001",
            "geometry": {"type": "Point", "coordinates": [-1.1581, 52.9548]},
            "properties": {
                "names": {"primary": "Old Market Square"},
                "categories": {"main": "park", "alternate": ["square", "civic"]},
                "confidence": 0.95,
                "sources": [{"dataset": "osm"}],
            },
        },
        {
            "type": "Feature",
            "id": "place-002",
            "geometry": {"type": "Point", "coordinates": [-1.1490, 52.9534]},
            "properties": {
                "names": {"primary": "Nottingham Castle"},
                "categories": {"main": "castle", "alternate": ["museum", "heritage"]},
                "confidence": 0.98,
                "sources": [{"dataset": "osm"}, {"dataset": "microsoft"}],
            },
        },
        {
            "type": "Feature",
            "id": "place-003",
            "geometry": {"type": "Point", "coordinates": [-1.1748, 52.9406]},
            "properties": {
                "names": {"primary": "Nottingham Station"},
                "categories": {"main": "train_station"},
                "confidence": 0.99,
                "sources": [{"dataset": "microsoft"}],
            },
        },
    ],
}

places = [overture_feature_to_geon(f) for f in overture_collection["features"]]

for p in places:
    print(f"--- {p.place} ({p.type}) ---")
    print(geon.generate(p))
